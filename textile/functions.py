#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
Copyright (c) 2009, Jason Samsa, http://jsamsa.com/
Copyright (c) 2010, Kurt Raschke <kurt@kurtraschke.com>
Copyright (c) 2004, Roberto A. F. De Almeida, http://dealmeida.net/
Copyright (c) 2003, Mark Pilgrim, http://diveintomark.org/

Original PHP Version:
Copyright (c) 2003-2004, Dean Allen <dean@textism.com>
All rights reserved.

Thanks to Carlo Zottmann <carlo@g-blog.net> for refactoring
Textile's procedural code into a class framework

Additions and fixes Copyright (c) 2006 Alex Shiels http://thresholdstate.com/

"""

import re
import uuid
from sys import maxunicode


try:
    # Python 3
    from urllib.parse import urlparse, urlsplit, urlunsplit, quote, unquote
    from html.parser import HTMLParser
    xrange = range
    unichr = chr
    unicode = str
except (ImportError):
    # Python 2
    from urllib import quote, unquote
    from urlparse import urlparse, urlsplit, urlunsplit
    from HTMLParser import HTMLParser

from textile.tools import sanitizer, imagesize

# We're going to use the Python 2.7+ OrderedDict data type.  Import it if it's
# available, otherwise, use the included tool.
try:
    from collections import OrderedDict
except ImportError:
    from textile.tools import OrderedDict


def _normalize_newlines(string):
    out = string.strip()
    out = re.sub(r'\r\n', '\n', out)
    out = re.sub(r'\n{3,}', '\n\n', out)
    out = re.sub(r'\n\s*\n', '\n\n', out)
    out = re.sub(r'"$', '" ', out)
    return out


_glyph_defaults = {
    'quote_single_open':  '&#8216;',
    'quote_single_close': '&#8217;',
    'quote_double_open':  '&#8220;',
    'quote_double_close': '&#8221;',
    'apostrophe':         '&#8217;',
    'prime':              '&#8242;',
    'prime_double':       '&#8243;',
    'ellipsis':           '&#8230;',
    'ampersand':          '&amp;',
    'emdash':             '&#8212;',
    'endash':             '&#8211;',
    'dimension':          '&#215;',
    'trademark':          '&#8482;',
    'registered':         '&#174;',
    'copyright':          '&#169;',
    'half':               '&#189;',
    'quarter':            '&#188;',
    'threequarters':      '&#190;',
    'degrees':            '&#176;',
    'plusminus':          '&#177;',
    'fn_ref_pattern':     '<sup%(atts)s>%(marker)s</sup>',
    'fn_foot_pattern':    '<sup%(atts)s>%(marker)s</sup>',
    'nl_ref_pattern':     '<sup%(atts)s>%(marker)s</sup>',
}

class Textile(object):
    horizontal_align_re = r'(?:\<(?!>)|(?<!<)\>|\<\>|\=|[()]+(?! ))'
    vertical_align_re = r'[\-^~]'
    class_re = r'(?:\([^)\n]+\))'       # Don't allow classes/ids,
    language_re = r'(?:\[[^\]\n]+\])'   # languages,
    style_re = r'(?:\{[^}\n]+\})'       # or styles to span across newlines
    colspan_re = r'(?:\\\d+)'
    rowspan_re = r'(?:\/\d+)'
    align_re = r'(?:%s|%s)*' % (horizontal_align_re, vertical_align_re)
    table_span_re = r'(?:%s|%s)*' % (colspan_re, rowspan_re)
    c = r'(?:%s)*' % '|'.join([class_re, style_re, language_re,
        horizontal_align_re])
    lc = r'(?:%s)*' % '|'.join([class_re, style_re, language_re])

    pnct = r'[-!"#$%&()*+,/:;<=>?@\'\[\\\]\.^_`{|}~]'
    urlch = r'[\w"$\-_.+!*\'(),";\/?:@=&%#{}|\\^~\[\]`]'
    syms  = u'¤§µ¶†‡•∗∴◊♠♣♥♦'

    url_schemes = ('http', 'https', 'ftp', 'mailto')

    btag = ('bq', 'bc', 'notextile', 'pre', 'h[1-6]', 'fn\d+', 'p', '###')
    btag_lite = ('bq', 'bc', 'p')

    iAlign = {'<': 'float: left;',
              '>': 'float: right;',
              '=': 'display: block; margin: 0 auto;'}
    vAlign = {'^': 'top', '-': 'middle', '~': 'bottom'}
    hAlign = {'<': 'left', '=': 'center', '>': 'right', '<>': 'justify'}

    note_index = 1

    # We'll be searching for characters that need to be HTML-encoded to produce
    # properly valid html.
    # These are the defaults that work in most cases.  Below, we'll copy this
    # and modify the necessary pieces to make it work for characters at the
    # beginning of the string.
    glyph_search = [
            # apostrophe's
            re.compile(r"(^|\w)'(\w)", re.U),
            # back in '88
            re.compile(r"(\s)'(\d+\w?)\b(?!')", re.U),
            # single closing
            re.compile(r"(^|\S)'(?=\s|%s|$)" % pnct, re.U),
            # single opening
            re.compile(r"'", re.U),
            # double closing
            re.compile(r'(^|\S)"(?=\s|%s|$)' % pnct, re.U),
            # double opening
            re.compile(r'"'),
            # ellipsis
            re.compile(r'([^.]?)\.{3}', re.U),
            # ampersand
            re.compile(r'(\s)&(\s)', re.U),
            # em dash
            re.compile(r'(\s?)--(\s?)', re.U),
            # en dash
            re.compile(r'\s-(?:\s|$)', re.U),
            # dimension sign
            re.compile(r'(\d+)( ?)x( ?)(?=\d+)', re.U),
            # trademark
            re.compile(r'\b ?[([]TM[])]', re.I | re.U),
            # registered
            re.compile(r'\b ?[([]R[])]', re.I | re.U),
            # copyright
            re.compile(r'\b ?[([]C[])]', re.I | re.U),
            # 1/2
            re.compile(r'[([]1\/2[])]', re.I | re.U),
            # 1/4
            re.compile(r'[([]1\/4[])]', re.I | re.U),
            # 3/4
            re.compile(r'[([]3\/4[])]', re.I | re.U),
            # degrees
            re.compile(r'[([]o[])]', re.I | re.U),
            # plus/minus
            re.compile(r'[([]\+\/-[])]', re.I | re.U),
        ]

    # These are the changes that need to be made for characters that occur at
    # the beginning of the string.
    glyph_search_initial = list(glyph_search)
    # apostrophe's
    glyph_search_initial[0] = re.compile(r"(\w)'(\w)", re.U)
    # single closing
    glyph_search_initial[2] = re.compile(r"(\S)'(?=\s|%s|$)" % pnct, re.U)
    # double closing
    glyph_search_initial[4] = re.compile(r'(\S)"(?=\s|%s|$)' % pnct, re.U)



    glyph_replace = [x % _glyph_defaults for x in (
        r'\1%(apostrophe)s\2',                # apostrophe's
        r'\1%(apostrophe)s\2',                # back in '88
        r'\1%(quote_single_close)s',          # single closing
        r'%(quote_single_open)s',             # single opening
        r'\1%(quote_double_close)s',          # double closing
        r'%(quote_double_open)s',             # double opening
        r'\1%(ellipsis)s',                    # ellipsis
        r'\1%(ampersand)s\2',                 # ampersand
        r'\1%(emdash)s\2',                    # em dash
        r' %(endash)s ',                      # en dash
        r'\1\2%(dimension)s\3',               # dimension sign
        r'%(trademark)s',                     # trademark
        r'%(registered)s',                    # registered
        r'%(copyright)s',                     # copyright
        r'%(half)s',                          # 1/2
        r'%(quarter)s',                       # 1/4
        r'%(threequarters)s',                 # 3/4
        r'%(degrees)s',                       # degrees
        r'%(plusminus)s',                     # plus/minus
        r'<acronym title="\2">\1</acronym>',  # 3+ uppercase acronym
        r'<span class="caps">\1</span>\2',    # 3+ uppercase
    )]

    doctype_whitelist = ['html', 'xhtml', 'html5']

    def __init__(self, restricted=False, lite=False, noimage=False,
                 auto_link=False, get_sizes=False):
        """Textile properties that are common to regular textile and
        textile_restricted"""
        self.restricted = restricted
        self.lite = lite
        self.noimage = noimage
        self.get_sizes = get_sizes
        self.auto_link = auto_link
        self.fn = {}
        self.urlrefs = {}
        self.shelf = {}
        self.rel = ''
        self.html_type = 'xhtml'
        self.max_span_depth = 5

        if self.html_type == 'html5':
            self.glyph_replace[19] = r'<abbr title="\2">\1</abbr>'

    def textile(self, text, rel=None, head_offset=0, html_type='xhtml',
                sanitize=False):
        """
        >>> import textile
        >>> textile.textile('some textile')
        '\\t<p>some textile</p>'
        """
        html_type = html_type.lower()
        self.html_type = (html_type in self.doctype_whitelist and html_type or
                'xhtml')
        self.notes = OrderedDict()
        self.unreferencedNotes = OrderedDict()
        self.notelist_cache = OrderedDict()

        # regular expressions get hairy when trying to search for unicode
        # characters.
        # we need to know if there are unicode charcters in the text.
        # return True as soon as a unicode character is found, else, False
        self.text_has_unicode = next((True for c in text if ord(c) > 128),
                False)

        if self.text_has_unicode:
            uppers = []
            for i in xrange(maxunicode):
                c = unichr(i)
                if c.isupper():
                    uppers.append(c)
            uppers = r''.join(uppers)
            uppers_re_patterns = [
                    # 3+ uppercase acronym
                    r'\b([%s][%s0-9]{2,})\b(?:[(]([^)]*)[)])' % (uppers,
                        uppers),
                    # 3+ uppercase
                    r"""(?:(?<=^)|(?<=\s)|(?<=[>\(;-]))([%s]{3,})(\w*)(?=\s|%s|$)(?=[^">]*?(<|$))"""
                        % (uppers, self.pnct),
                    ]
        else:
            uppers_re_patterns = [
                    # 3+ uppercase acronym
                    r'\b([A-Z][A-Z0-9]{2,})\b(?:[(]([^)]*)[)])',
                    # 3+ uppercase
                    r"""(?:(?<=^)|(?<=\s)|(?<=[\>\(;-]))([A-Z]{3,})(\w*)(?=\s|%s|$)(?=[^">]*?(<|$))"""
                        % self.pnct,
                    ]

        uppers_re = [re.compile(x, re.U) for x in uppers_re_patterns]

        self.glyph_search += uppers_re
        self.glyph_search_initial += uppers_re

        # text = unicode(text)
        text = _normalize_newlines(text)

        if self.restricted:
            text = self.encode_html(text, quotes=False)

        if rel:
            self.rel = ' rel="%s"' % rel

        text = self.getRefs(text)

        # The original php puts the below within an if not self.lite, but our
        # block function handles self.lite itself.
        text = self.block(text, int(head_offset))

        if not self.lite:
            text = self.placeNoteLists(text)

        text = self.retrieve(text)

        if sanitize:
            text = sanitizer.sanitize(text, self.html_type)

        breaktag = {'html': '<br>', 'xhtml': '<br />'}

        text = text.replace(breaktag[self.html_type], '%s\n' % breaktag[self.html_type])

        return text

    def pba(self, block_attributes, element=None):
        """
        Parse block attributes.

        >>> t = Textile()
        >>> t.pba(r'\3')
        ''
        >>> t.pba(r'\\3', element='td')
        ' colspan="3"'
        >>> t.pba(r'/4', element='td')
        ' rowspan="4"'
        >>> t.pba(r'\\3/4', element='td')
        ' colspan="3" rowspan="4"'

        >>> t.pba('^', element='td')
        ' style="vertical-align:top;"'

        >>> t.pba('{line-height:18px}')
        ' style="line-height:18px;"'

        >>> t.pba('(foo-bar)')
        ' class="foo-bar"'

        >>> t.pba('(#myid)')
        ' id="myid"'

        >>> t.pba('(foo-bar#myid)')
        ' class="foo-bar" id="myid"'

        >>> t.pba('((((')
        ' style="padding-left:4em;"'

        >>> t.pba(')))')
        ' style="padding-right:3em;"'

        >>> t.pba('[fr]')
        ' lang="fr"'

        >>> t.pba(r'\\5 80', 'col')
        ' span="5" width="80"'

        >>> rt = Textile()
        >>> rt.restricted = True
        >>> rt.pba('[en]')
        ' lang="en"'

        >>> rt.pba('(#id)')
        ''

        """
        style = []
        aclass = ''
        lang = ''
        colspan = ''
        rowspan = ''
        block_id = ''
        span = ''
        width = ''

        if not block_attributes:
            return ''

        matched = block_attributes
        if element == 'td':
            m = re.search(r'\\(\d+)', matched)
            if m:
                colspan = m.group(1)

            m = re.search(r'/(\d+)', matched)
            if m:
                rowspan = m.group(1)

        if element == 'td' or element == 'tr':
            m = re.search(r'(%s)' % self.vertical_align_re, matched)
            if m:
                style.append("vertical-align:%s" % self.vAlign[m.group(1)])

        m = re.search(r'\{([^}]*)\}', matched)
        if m:
            style += m.group(1).rstrip(';').split(';')
            matched = matched.replace(m.group(0), '')

        m = re.search(r'\[([^\]]+)\]', matched, re.U)
        if m:
            lang = m.group(1)
            matched = matched.replace(m.group(0), '')

        m = re.search(r'\(([^()]+)\)', matched, re.U)
        if m:
            aclass = m.group(1)
            matched = matched.replace(m.group(0), '')

        m = re.search(r'([(]+)', matched)
        if m:
            style.append("padding-left:%sem" % len(m.group(1)))
            matched = matched.replace(m.group(0), '')

        m = re.search(r'([)]+)', matched)
        if m:
            style.append("padding-right:%sem" % len(m.group(1)))
            matched = matched.replace(m.group(0), '')

        m = re.search(r'(%s)' % self.horizontal_align_re, matched)
        if m:
            style.append("text-align:%s" % self.hAlign[m.group(1)])

        m = re.search(r'^(.*)#(.*)$', aclass)
        if m:
            block_id = m.group(2)
            aclass = m.group(1)

        if element == 'col':
            pattern = r'(?:\\(\d+))?\s*(\d+)?'
            csp = re.match(pattern, matched)
            span, width = csp.groups()

        if self.restricted:
            if lang:
                return ' lang="%s"' % lang
            else:
                return ''

        result = []
        if style:
            # Previous splits that created style may have introduced extra
            # whitespace into the list elements.  Clean it up.
            style = [x.strip() for x in style]
            result.append(' style="%s;"' % "; ".join(style))
        if aclass:
            result.append(' class="%s"' % aclass)
        if block_id:
            result.append(' id="%s"' % block_id)
        if lang:
            result.append(' lang="%s"' % lang)
        if colspan:
            result.append(' colspan="%s"' % colspan)
        if rowspan:
            result.append(' rowspan="%s"' % rowspan)
        if span:
            result.append(' span="%s"' % span)
        if width:
            result.append(' width="%s"' % width)
        return ''.join(result)

    def hasRawText(self, text):
        """
        checks whether the text has text not already enclosed by a block tag

        >>> t = Textile()
        >>> t.hasRawText('<p>foo bar biz baz</p>')
        False

        >>> t.hasRawText(' why yes, yes it does')
        True

        """
        r = re.compile(r'<(p|blockquote|div|form|table|ul|ol|dl|pre|h\d)[^>]*?>.*</\1>',
                       re.S).sub('', text.strip()).strip()
        r = re.compile(r'<(hr|br)[^>]*?/>').sub('', r)
        return '' != r

    def table(self, text):
        r"""
        >>> t = Textile()
        >>> t.table('(rowclass). |one|two|three|\n|a|b|c|')
        '\t<table>\n\t\t<tr class="rowclass">\n\t\t\t<td>one</td>\n\t\t\t<td>two</td>\n\t\t\t<td>three</td>\n\t\t</tr>\n\t\t<tr>\n\t\t\t<td>a</td>\n\t\t\t<td>b</td>\n\t\t\t<td>c</td>\n\t\t</tr>\n\t</table>\n\n'
        """
        text = text + "\n\n"
        pattern = re.compile(r'^(?:table(_?%(s)s%(a)s%(c)s)\.(.*?)\n)?^(%(a)s%(c)s\.? ?\|.*\|)[\s]*\n\n'
                             % {'s': self.table_span_re,
                                'a': self.align_re,
                                'c': self.c},
                             re.S | re.M | re.U)
        return pattern.sub(self.fTable, text)

    def fTable(self, match):
        tatts = self.pba(match.group(1), 'table')

        summary = ' summary="%s"' % match.group(2).strip() if match.group(2) else ''
        cap = ''
        colgrp, last_rgrp = '', ''
        c_row = 1
        rows = []
        for row in [x for x in re.split(r'\|\s*?$', match.group(3), flags=re.M) if x]:
            row = row.lstrip()

            # Caption -- only occurs on row 1, otherwise treat '|=. foo |...'
            # as a normal center-aligned cell.
            captionpattern = r"^\|\=(%(s)s%(a)s%(c)s)\. ([^\n]*)(.*)" % {'s':
                    self.table_span_re, 'a': self.align_re, 'c': self.c}
            caption_re = re.compile(captionpattern, re.S)
            cmtch = caption_re.match(row)
            if c_row ==1 and cmtch:
                capatts = self.pba(cmtch.group(1))
                cap = "\t<caption%s>%s</caption>\n" % (capatts, cmtch.group(2).strip())
                row = cmtch.group(3).lstrip()
                if row == '':
                    continue

            c_row += 1

            # Colgroup
            grppattern = r"^\|:(%(s)s%(a)s%(c)s\. .*)" % {'s': self.table_span_re, 'a':
                    self.align_re, 'c': self.c}
            grp_re = re.compile(grppattern, re.M)
            gmtch = grp_re.match(row.lstrip())
            if gmtch:
                has_newline = "\n" in row
                idx = 0
                for col in gmtch.group(1).replace('.', '').split("|"):
                    gatts = self.pba(col.strip(), 'col')
                    if idx == 0:
                        gatts = "group%s>" % gatts
                    else:
                        gatts = gatts + " />"
                    colgrp = colgrp + "\t<col%s\n" % gatts
                    idx += 1
                colgrp += "\t</colgroup>\n"


                # If the row has a newline in it, account for the missing
                # closing pipe and process the rest of the line
                if not has_newline:
                    continue
                else:
                    row = row[row.index('\n'):].lstrip()

            grpmatchpattern = (r"(:?^\|(%(v)s)(%(s)s%(a)s%(c)s)\.\s*$\n)?^(.*)"
                    % {'v': self.vertical_align_re,'s': self.table_span_re,
                        'a': self.align_re, 'c': self.c})
            grpmatch_re = re.compile(grpmatchpattern, re.S | re.M)
            grpmatch = grpmatch_re.match(row.lstrip())

            # Row group
            rgrp = ''
            rgrptypes = {'^': 'head', '~': 'foot', '-': 'body'}
            if grpmatch.group(2):
                rgrp = rgrptypes[grpmatch.group(2)]
            rgrpatts = self.pba(grpmatch.group(3))
            row = grpmatch.group(4)

            rmtch = re.search(r'^(%s%s\. )(.*)'
                              % (self.align_re, self.c), row.lstrip())
            if rmtch:
                ratts = self.pba(rmtch.group(1), 'tr')
                row = rmtch.group(2)
            else:
                ratts = ''

            cells = []
            cellctr = 0
            for cell in row.split('|'):
                ctyp = 'd'
                if re.search(r'^_', cell):
                    ctyp = "h"
                cmtch = re.search(r'^(_?%s%s%s\. )(.*)' % (self.table_span_re,
                    self.align_re, self.c), cell)
                if cmtch:
                    catts = self.pba(cmtch.group(1), 'td')
                    cell = cmtch.group(2)
                else:
                    catts = ''

                if not self.lite:
                    cell = self.redcloth_list(cell)
                    cell = self.lists(cell)

                # row.split() gives us ['', 'cell 1 contents', '...']
                # so we ignore the first cell.
                if cellctr > 0:
                    ctag = "t%s" % ctyp
                    cline = ("\t\t\t<%(ctag)s%(catts)s>%(cell)s</%(ctag)s>"
                            % {'ctag': ctag, 'catts': catts, 'cell': cell})
                    cells.append(self.doTagBr(ctag, cline))

                cellctr += 1

            if rgrp and last_rgrp:
                grp = "\t</t%s>\n" % last_rgrp
            else:
                grp = ''

            if rgrp:
                grp += "\t<t%s%s>\n" % (rgrp, rgrpatts)

            last_rgrp = rgrp if rgrp else last_rgrp

            rows.append("%s\t\t<tr%s>\n%s%s\t\t</tr>" % (grp, ratts,
                '\n'.join(cells), '\n' if cells else ''))
            cells = []
            catts = None

        if last_rgrp:
            last_rgrp = '\t</t%s>\n' % last_rgrp
        tbl = ("\t<table%(tatts)s%(summary)s>\n%(cap)s%(colgrp)s%(rows)s\n%(last_rgrp)s\t</table>\n\n"
                % {'tatts': tatts, 'summary': summary, 'cap': cap, 'colgrp':
                    colgrp, 'last_rgrp': last_rgrp, 'rows': '\n'.join(rows)})
        return tbl

    def lists(self, text):
        """
        >>> t = Textile()
        >>> t.lists("* one\\n* two\\n* three")
        '\\t<ul>\\n\\t\\t<li>one</li>\\n\\t\\t<li>two</li>\\n\\t\\t<li>three</li>\\n\\t</ul>'
        """

        #Replace line-initial bullets with asterisks
        bullet_pattern = re.compile(u'^•', re.U | re.M)

        pattern = re.compile(r'^((?:[*;:]+|[*;:#]*#(?:_|\d+)?)%s[ .].*)$(?![^#*;:])'
                             % self.lc, re.U | re.M | re.S)
        return pattern.sub(self.fList, bullet_pattern.sub('*', text))

    def fList(self, match):
        text = re.split(r'\n(?=[*#;:])', match.group(), flags=re.M)
        pt = ''
        result = []
        ls = OrderedDict()
        for i, line in enumerate(text):
            try:
                nextline = text[i + 1]
            except IndexError:
                nextline = ''

            m = re.search(r"^([#*;:]+)(_|\d+)?(%s)[ .](.*)$" % self.lc, line,
                    re.S)
            if m:
                tl, start, atts, content = m.groups()
                content = content.strip()
                nl = ''
                ltype = self.listType(tl)
                if ';' in tl:
                    litem = 'dt'
                elif ':' in tl:
                    litem = 'dd'
                else:
                    litem = 'li'

                showitem = len(content) > 0

                # handle list continuation/start attribute on ordered lists
                if ltype == 'o':
                    if not hasattr(self, 'olstarts'):
                        self.olstarts = {tl: 1}

                    # does the first line of this ol have a start attribute
                    if len(tl) > len(pt):
                        # no, set it to 1
                        if start is None:
                            self.olstarts[tl] = 1
                        # yes, set it to the given number
                        elif start != '_':
                            self.olstarts[tl] = int(start)
                        # we won't need to handle the '_' case, we'll just
                        # print out the number when it's needed

                    # put together the start attribute if needed
                    if len(tl) > len(pt) and start is not None:
                        start = ' start="%s"' % self.olstarts[tl]

                    # This will only increment the count for list items, not
                    # definition items
                    if showitem:
                        self.olstarts[tl] += 1

                nm = re.match("^([#\*;:]+)(_|[\d]+)?%s[ .].*" % self.lc,
                        nextline)
                if nm:
                    nl = nm.group(1)

                # We need to handle nested definition lists differently.
                # If the next tag is a dt (';') of a lower ensted level than the current dd (':'),
                #if (';' in nl and ':' in tl) and len(nl) < len(tl):
                if ';' in pt and ':' in tl:
                    ls[tl] = 2

                atts = self.pba(atts)
                # If start is still None, set it to '', else leave the value
                # that we've already formatted.
                start = start or ''

                # if this item tag isn't in the list, create a new list and
                # item, else just create the item
                if tl not in ls:
                    ls[tl] = 1
                    itemtag = "\n\t\t<%s>%s" % (litem, content) if showitem else ''
                    line = "\t<%sl%s%s>%s" % (ltype, atts, start, itemtag)
                else:
                    line = "\t\t<%s%s>%s" % (litem, atts, content) if showitem else ''

                if len(nl) <= len(tl):
                    line = line + ("</%s>" % litem if showitem else '')
                # work backward through the list closing nested lists/items
                for k, v in reversed(list(ls.items())):
                    if len(k) > len(nl):
                        if v != 2:
                            line = line + "\n\t</%sl>" % self.listType(k)
                        if len(k) > 1 and v != 2:
                            line = line + "</%s>" % litem
                        del ls[k]

                # Remember the current Textile tag
                pt = tl

            # This else exists in the original php version.  I'm not sure how
            # to come up with a case where the line would not match.  I think
            # it may have been necessary due to the way php returns matches.
            #else:
                #line = line + "\n"
            result.append(line)
        return self.doTagBr(litem, "\n".join(result))

    def listType(self, list_string):
        listtypes = {
                list_string.startswith('*'): 'u',
                list_string.startswith('#'): 'o',
                not list_string.startswith('*') and not list_string.startswith('#'): 'd'
                }
        return listtypes[True]

    def doTagBr(self, tag, input):
        return re.compile(r'<(%s)([^>]*?)>(.*)(</\1>)' % re.escape(tag),
                re.S).sub(self.doBr, input)

    def doPBr(self, in_):
        return re.compile(r'<(p)([^>]*?)>(.*)(</\1>)', re.S).sub(self.doBr,
                                                                 in_)

    def doBr(self, match):
        content = re.sub(r'(.+)(?:(?<!<br>)|(?<!<br />))\n(?![#*;:\s|])', r'\1<br />',
                             match.group(3))
        return '<%s%s>%s%s' % (match.group(1), match.group(2),
                               content, match.group(4))

    def block(self, text, head_offset=0):
        """
        >>> t = Textile()
        >>> t.block('h1. foobar baby')
        '\\t<h1>foobar baby</h1>'
        """
        if not self.lite:
            tre = '|'.join(self.btag)
        else:
            tre = '|'.join(self.btag_lite)
        text = text.split('\n\n')

        tag = 'p'
        atts = cite = graf = ext = ''
        c1 = ''

        out = []

        anon = False
        for line in text:
            pattern = r'^(%s)(%s%s)\.(\.?)(?::(\S+))? (.*)$' % (tre,
                    self.align_re, self.c)
            match = re.search(pattern, line, re.S)
            if match:
                if ext:
                    out.append(out.pop() + c1)

                tag, atts, ext, cite, graf = match.groups()
                h_match = re.search(r'h([1-6])', tag)
                if h_match:
                    head_level, = h_match.groups()
                    tag = 'h%i' % max(1, min(int(head_level) + head_offset, 6))
                o1, o2, content, c2, c1, eat = self.fBlock(tag, atts, ext,
                                                      cite, graf)
                # leave off c1 if this block is extended,
                # we'll close it at the start of the next block

                if ext:
                    line = "%s%s%s%s" % (o1, o2, content, c2)
                else:
                    line = "%s%s%s%s%s" % (o1, o2, content, c2, c1)

            else:
                anon = True
                if ext or not re.search(r'^\s', line):
                    o1, o2, content, c2, c1, eat = self.fBlock(tag, atts, ext,
                                                          cite, line)
                    # skip $o1/$c1 because this is part of a continuing
                    # extended block
                    if tag == 'p' and not self.hasRawText(content):
                        line = content
                    else:
                        line = "%s%s%s" % (o2, content, c2)
                else:
                    line = self.graf(line)

            line = self.doPBr(line)
            if self.html_type == 'xhtml':
                line = re.sub(r'<br>', '<br />', line)

            if self.html_type == 'html':
                line = re.sub(r'<br />', '<br>', line)

            if ext and anon:
                out.append(out.pop() + "\n" + line)
            elif not eat:
                out.append(line)

            if not ext:
                tag = 'p'
                atts = ''
                cite = ''
                graf = ''

        if ext:
            out.append(out.pop() + c1)
        return '\n\n'.join(out)

    def fBlock(self, tag, atts, ext, cite, content):
        """
        >>> t = Textile()
        >>> t.fBlock("bq", "", None, "", "Hello BlockQuote")
        ('\\t<blockquote>\\n', '\\t\\t<p>', 'Hello BlockQuote', '</p>', '\\n\\t</blockquote>', False)

        >>> t.fBlock("bq", "", None, "http://google.com", "Hello BlockQuote")
        ('\\t<blockquote cite="http://google.com">\\n', '\\t\\t<p>', 'Hello BlockQuote', '</p>', '\\n\\t</blockquote>', False)

        >>> t.fBlock("bc", "", None, "", 'printf "Hello, World";') # doctest: +ELLIPSIS
        ('<pre>', '<code>', ..., '</code>', '</pre>', False)

        >>> t.fBlock("h1", "", None, "", "foobar")
        ('', '\\t<h1>', 'foobar', '</h1>', '', False)
        """
        att = atts
        atts = self.pba(atts)
        o1 = o2 = c2 = c1 = ''
        eat = False

        if tag == 'p':
            # is this an anonymous block with a note definition?
            notedef_re = re.compile(r"""
            ^note\#                 # start of note def marker
            ([^%%<*!@#^([{ \s.]+)   # !label
            ([*!^]?)                # !link
            (%s)                    # !att
            \.?                     # optional period.
            [\s]+                   # whitespace ends def marker
            (.*)$                   # !content""" % (self.c), re.X)
            notedef = notedef_re.sub(self.fParseNoteDefs, content)

            # It will be empty if the regex matched and ate it.
            if '' == notedef:
                return o1, o2, notedef, c2, c1, True

        m = re.search(r'fn(\d+)', tag)
        if m:
            tag = 'p'
            if m.group(1) in self.fn:
                fnid = self.fn[m.group(1)]
            else:
                fnid = m.group(1)

            # If there is an author-specified ID goes on the wrapper & the
            # auto-id gets pushed to the <sup>
            supp_id = ''

            # if class has not been previously specified, set it to "footnote"
            if atts.find('class=') < 0:
                atts = atts + ' class="footnote"'

            # if there's no specified id, use the generated one.
            if atts.find('id=') < 0:
                atts = atts + ' id="fn%s"' % fnid
            else:
                supp_id = ' id="fn%s"' % fnid

            if att.find('^') < 0:
                sup = self.formatFootnote(m.group(1), supp_id)
            else:
                fnrev = '<a href="#fnrev%s">%s</a>' % (fnid, m.group(1))
                sup = self.formatFootnote(fnrev, supp_id)

            content = sup + ' ' + content

        if tag == 'bq':
            cite = self.checkRefs(cite)
            if cite:
                cite = ' cite="%s"' % cite
            else:
                cite = ''
            o1 = "\t<blockquote%s%s>\n" % (cite, atts)
            o2 = "\t\t<p%s>" % atts
            c2 = "</p>"
            c1 = "\n\t</blockquote>"

        elif tag == 'bc':
            o1 = "<pre%s>" % atts
            o2 = "<code%s>" % atts
            c2 = "</code>"
            c1 = "</pre>"
            content = self.shelve(self.encode_html(content.rstrip("\n") +
                                                   "\n"))

        elif tag == 'notextile':
            content = self.shelve(content)
            o1 = o2 = ''
            c1 = c2 = ''

        elif tag == 'pre':
            content = self.shelve(self.encode_html(content.rstrip("\n") +
                                                   "\n"))
            o1 = "<pre%s>" % atts
            o2 = c2 = ''
            c1 = '</pre>'

        elif tag == '###':
            eat = True

        else:
            o2 = "\t<%s%s>" % (tag, atts)
            c2 = "</%s>" % tag

        if not eat:
            content = self.graf(content)
        else:
            content = ''
        return o1, o2, content, c2, c1, eat

    def formatFootnote(self, marker, atts='', anchor=True):
        if anchor:
            pattern = _glyph_defaults['fn_foot_pattern']
        else:
            pattern = _glyph_defaults['fn_ref_pattern']
        return pattern % {'atts': atts, 'marker': marker}

    def footnoteRef(self, text):
        """
        >>> t = Textile()
        >>> t.footnoteRef('foo[1] ') # doctest: +ELLIPSIS
        'foo<sup class="footnote" id="fnrev..."><a href="#fn...">1</a></sup> '
        """
        return re.compile(r'(?<=\S)\[(\d+)(!?)\](\s)?', re.U).sub(
                self.footnoteID, text)

    def footnoteID(self, match):
        footnoteNum, nolink, space = match.groups()
        if not space:
            space = ''
        backref = ' class="footnote"'
        if footnoteNum not in self.fn:
            a = str(uuid.uuid4()).replace('-', '')
            self.fn[footnoteNum] = a
            backref = '%s id="fnrev%s"' % (backref, a)
        footnoteID = self.fn[footnoteNum]
        footref = '!' == nolink and footnoteNum or '<a href="#fn%s">%s</a>' % (
                footnoteID, footnoteNum)
        footref = self.formatFootnote(footref, backref, False)
        return footref + space

    def glyphs(self, text):
        """
        Because of the split command, the regular expressions are different for
        when the text at the beginning and the rest of the text.
        for example:
        let's say the raw text provided is "*Here*'s some textile"
        before it gets to this glyphs method, the text has been converted to
        "<strong>Here</strong>'s some textile"
        When run through the split, we end up with ["<strong>", "Here",
        "</strong>", "'s some textile"].  The re.search that follows tells it
        not to ignore html tags.
        If the single quote is the first character on the line, it's an open
        single quote.  If it's the first character of one of those splits, it's
        an apostrophe or closed single quote, but the regex will bear that out.
        A similar situation occurs for double quotes as well.
        So, for the first pass, we use the glyph_search_initial set of
        regexes.  For all remaining passes, we use glyph_search

        >>> t = Textile()

        >>> t.glyphs("apostrophe's")
        'apostrophe&#8217;s'

        >>> t.glyphs("back in '88")
        'back in &#8217;88'

        >>> t.glyphs('foo ...')
        'foo &#8230;'

        >>> t.glyphs('--')
        '&#8212;'

        >>> t.glyphs('FooBar[tm]')
        'FooBar&#8482;'

        >>> t.glyphs("<p><cite>Cat's Cradle</cite> by Vonnegut</p>")
        '<p><cite>Cat&#8217;s Cradle</cite> by Vonnegut</p>'

        """
        # fix: hackish
        text = re.sub(r'"\Z', r'" ', text)

        result = []
        searchlist = self.glyph_search_initial
        for i, line in enumerate(re.compile(r'(<[\w\/!?].*?>)', re.U).split(text)):
            if not i % 2:
                for s, r in zip(searchlist, self.glyph_replace):
                    line = s.sub(r, line)
            result.append(line)
            if i == 0:
                searchlist = self.glyph_search
        return ''.join(result)

    def getRefs(self, text):
        """
        Capture and store URL references in self.urlrefs.

        >>> t = Textile()
        >>> t.getRefs("some text [Google]http://www.google.com")
        'some text '
        >>> t.urlrefs
        {'Google': 'http://www.google.com'}

        """
        pattern = re.compile(r'(?:(?<=^)|(?<=\s))\[(.+)\]((?:http(?:s?):\/\/|\/)\S+)(?=\s|$)', re.U)
        text = pattern.sub(self.refs, text)
        return text

    def refs(self, match):
        flag, url = match.groups()
        self.urlrefs[flag] = url
        return ''

    def checkRefs(self, url):
        return self.urlrefs.get(url, url)

    def isRelURL(self, url):
        """
        Identify relative urls.

        >>> t = Textile()
        >>> t.isRelURL("http://www.google.com/")
        False
        >>> t.isRelURL("/foo")
        True

        """
        (scheme, netloc) = urlparse(url)[0:2]
        return not scheme and not netloc

    def relURL(self, url):
        """
        >>> t = Textile()
        >>> t.relURL("http://www.google.com/")
        'http://www.google.com/'
        >>> t.restricted = True
        >>> t.relURL("gopher://gopher.com/")
        '#'

        """
        scheme = urlparse(url)[0]
        if self.restricted and scheme and scheme not in self.url_schemes:
            return '#'
        return url

    def shelve(self, text):
        itemID = str(uuid.uuid4()).replace('-', '')
        self.shelf[itemID] = text
        return itemID

    def retrieve(self, text):
        """
        >>> t = Textile()
        >>> id = t.shelve("foobar")
        >>> t.retrieve(id)
        'foobar'
        """
        while True:
            old = text
            for k, v in self.shelf.items():
                text = text.replace(k, v)
            if text == old:
                break
        return text

    def encode_html(self, text, quotes=True):
        """Return text that's safe for an HTML attribute.
        >>> t = Textile()
        >>> t.encode_html('this is a "test" of text that\\\'s safe to put in an <html> attribute.')
        'this is a &#34;test&#34; of text that&#39;s safe to put in an &lt;html&gt; attribute.'
        """
        a = (
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'))

        if quotes:
            a = a + (("'", '&#39;'),
                     ('"', '&#34;'))

        for k, v in a:
            text = text.replace(k, v)
        return text

    def graf(self, text):
        if not self.lite:
            text = self.noTextile(text)
            text = self.code(text)

        text = self.getHTMLComments(text)

        text = self.getRefs(text)
        text = self.links(text)
        if self.auto_link:
            text = self.autoLink(text)
            text = self.links(text)

        if not self.noimage:
            text = self.image(text)


        if not self.lite:
            text = self.table(text)
            text = self.redcloth_list(text)
            text = self.lists(text)

        text = self.span(text)
        text = self.footnoteRef(text)
        text = self.noteRef(text)
        text = self.glyphs(text)

        return text.rstrip('\n')

    def autoLink(self, text):
        """
        >>> t = Textile()
        >>> t.autoLink("http://www.ya.ru")
        '"$":http://www.ya.ru'
        """

        pattern = re.compile(r"""\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""", re.U | re.I)
        return pattern.sub(r'"$":\1', text)

    def links(self, text):
        """
        >>> t = Textile()
        >>> t.links('fooobar "Google":http://google.com/foobar/ and hello world "flickr":http://flickr.com/photos/jsamsa/ ') # doctest: +ELLIPSIS
        'fooobar ... and hello world ...'
        """

        # For some reason, the part of the regex below that matches the url
        # does not match a trailing parenthesis.  It gets caught by tail, and
        # we check later to see if it should be included as part of the url.
        pattern = r'''
            (?P<pre>^|(?<=[\s>.\(\|])|[{[])?    # leading text
            "                                   # opening quote
            (?P<atts>%s)                        # block attributes
            (?P<text>[^"]+?)                    # link text
            \s?                                 # optional space
            (?:\((?P<title>[^)]+?)\)(?="))?     # optional title
            ":                                  # closing quote, colon
            (?P<url>%s+?)                       # URL
            (?P<slash>\/)?                      # slash
            (?P<post>[^\w\/]*?)                 # trailing text
            (?P<tail>[\]})]|(?=\s|$|\|))        # tail
        ''' % (self.c, self.urlch)

        text = re.compile(pattern, re.X | re.U).sub(self.fLink, text)

        return text

    def fLink(self, match):
        pre, atts, text, title, url, slash, post, tail = match.groups()

        if not pre:
            pre = ''

        if not slash:
            slash = ''

        if text == '$':
            text = re.sub(r'^\w+://(.+)', r'\1', url)

        # assume ) at the end of the url is not actually part of the url
        # unless the url also contains a (
        if tail == ')' and url.find('(') > -1:
            url = url + tail
            tail = None

        url = self.checkRefs(url)
        try:
            url = self.encode_url(url)
        except:
            pass

        atts = self.pba(atts)
        if title:
            atts = atts + ' title="%s"' % self.encode_html(title)

        if not self.noimage:
            text = self.image(text)

        text = self.span(text)
        text = self.glyphs(text)

        url = self.relURL(url) + slash
        out = '<a href="%s"%s%s>%s</a>' % (self.encode_html(url), atts,
                self.rel, text)

        if (pre and not tail) or (tail and not pre):
            out = ''.join([pre, out, post, tail])
            post = ''

        out = self.shelve(out)
        return ''.join([out, post])

    def encode_url(self, url):
        """
        Converts a (unicode) URL to an ASCII URL, with the domain part
        IDNA-encoded and the path part %-encoded (as per RFC 3986).

        Fixed version of the following code fragment from Stack Overflow:
        http://stackoverflow.com/questions/804336/best-way-to-convert-a-unicode-url-to-ascii-utf-8-percent-escaped-in-python/804380#804380
        """
        # turn string into unicode
        if not isinstance(url, unicode):
            url = url.decode('utf8')

        # parse it
        parsed = urlsplit(url)

        # divide the netloc further
        netloc_pattern = re.compile(r"""
            (?:(?P<user>[^:@]+)(?::(?P<password>[^:@]+))?@)?
            (?P<host>[^:]+)
            (?::(?P<port>[0-9]+))?
        """, re.X | re.U)
        netloc_parsed = netloc_pattern.match(parsed.netloc).groupdict()

        # encode each component
        scheme = parsed.scheme
        user = netloc_parsed['user'] and quote(netloc_parsed['user'])
        password = netloc_parsed['password'] and quote(netloc_parsed['password'])
        host = netloc_parsed['host']
        port = netloc_parsed['port'] and netloc_parsed['port']
        path = '/'.join(  # could be encoded slashes!
            quote(unquote(pce),'')
            for pce in parsed.path.split('/')
        )
        query = quote(unquote(parsed.query), '=&?/')
        fragment = quote(unquote(parsed.fragment))

        # put it back together
        netloc = ''
        if user:
            netloc += user
            if password:
                netloc += ':' + password
            netloc += '@'
        netloc += host
        if port:
            netloc += ':'+port
        return urlunsplit((scheme, netloc, path, query, fragment))

    def span(self, text):
        """
        >>> t = Textile()
        >>> t.span(r"hello %(bob)span *strong* and **bold**% goodbye")
        'hello <span class="bob">span <strong>strong</strong> and <b>bold</b></span> goodbye'
        """
        qtags = (r'\*\*', r'\*', r'\?\?', r'\-', r'__',
                 r'_', r'%', r'\+', r'~', r'\^')
        pnct = ".,\"'?!;:("

        for qtag in qtags:
            pattern = re.compile(r"""
                (?:^|(?<=[\s>%(pnct)s])|([\[{]))
                (%(qtag)s)(?!%(qtag)s)
                (%(c)s)
                (?::\(([^)]+?)\))?
                ([^\s%(qtag)s]+|\S[^%(qtag)s\n]*[^\s%(qtag)s\n])
                ([%(pnct)s]*)
                %(qtag)s
                (?:$|([\]}])|(?=%(selfpnct)s{1,2}|\s))
            """ % {'qtag': qtag, 'c': self.c, 'pnct': pnct,
                   'selfpnct': self.pnct}, re.X)
            text = pattern.sub(self.fSpan, text)
        return text

    def fSpan(self, match):
        _, tag, atts, cite, content, end, _ = match.groups()

        qtags = {'*': 'strong',
                '**': 'b',
                '??': 'cite',
                 '_': 'em',
                '__': 'i',
                 '-': 'del',
                 '%': 'span',
                 '+': 'ins',
                 '~': 'sub',
                 '^': 'sup'}

        tag = qtags[tag]
        atts = self.pba(atts)
        if cite:
            atts = atts + ' cite="%s"' % cite

        content = self.span(content)

        out = "<%s%s>%s%s</%s>" % (tag, atts, content, end, tag)
        return out

    def image(self, text):
        """
        >>> t = Textile()
        >>> t.image('!/imgs/myphoto.jpg!:http://jsamsa.com')
        '<a href="http://jsamsa.com" class="img"><img alt="" src="/imgs/myphoto.jpg" /></a>'
        >>> t.image('!</imgs/myphoto.jpg!')
        '<img align="left" alt="" src="/imgs/myphoto.jpg" />'
        """
        pattern = re.compile(r"""
            (?:[\[{])?         # pre
            \!                 # opening !
            (\<|\=|\>)?        # optional alignment atts
            (%s)               # optional style,class atts
            (?:\. )?           # optional dot-space
            ([^\s(!]+)         # presume this is the src
            \s?                # optional space
            (?:\(([^\)]+)\))?  # optional title
            \!                 # closing
            (?::(\S+))?        # optional href
            (?:[\]}]|(?=\s|$)) # lookahead: space or end of string
        """ % self.c, re.U | re.X)
        return pattern.sub(self.fImage, text)

    def fImage(self, match):
        # (None, '', '/imgs/myphoto.jpg', None, None)
        align, atts, url, title, href = match.groups()
        atts = self.pba(atts)
        size = None

        alignments = {'<': 'left', '=': 'center', '>': 'right'}

        if  not title:
            title = ''

        if not self.isRelURL(url) and self.get_sizes:
            size = imagesize.getimagesize(url)

        if href:
            href = self.checkRefs(href)

        url = self.checkRefs(url)
        url = self.relURL(url)

        out = []
        if href:
            out.append('<a href="%s" class="img">' % href)
        out.append('<img')
        if align:
            out.append(' align="%s"' % alignments[align])
        out.append(' alt="%s"' % title)
        if size:
            out.append(' height="%s"' % size[1])
        out.append(' src="%s"' % url)
        if title:
            out.append(' title="%s"' % title)
        if size:
            out.append(' width="%s"' % size[0])
        if self.html_type == 'html':
            out.append('>')
        else:
            out.append(' />')
        if href:
            out.append('</a>')

        return ''.join(out)

    def code(self, text):
        text = self.doSpecial(text, '<code>', '</code>', self.fCode)
        text = self.doSpecial(text, '@', '@', self.fCode)
        text = self.doSpecial(text, '<pre>', '</pre>', self.fPre)
        return text

    def fCode(self, match):
        before, text, after = match.groups()
        if after == None:
            after = ''
        # text needs to be escaped
        if not self.restricted:
            text = self.encode_html(text, quotes=False)
        return ''.join([before, self.shelve('<code>%s</code>' % text), after])

    def fPre(self, match):
        before, text, after = match.groups()
        if after == None:
            after = ''
        # text needs to be escaped
        if not self.restricted:
            text = self.encode_html(text)
        return ''.join([before, '<pre>', self.shelve(text), '</pre>', after])

    def doSpecial(self, text, start, end, method):
        pattern = re.compile(r'(^|\s|[\[({>|])%s(.*?)%s($|[\])}])?'
                             % (re.escape(start), re.escape(end)), re.M | re.S)
        return pattern.sub(method, text)

    def noTextile(self, text):
        text = self.doSpecial(text, '<notextile>', '</notextile>',
                              self.fTextile)
        return self.doSpecial(text, '==', '==', self.fTextile)

    def fTextile(self, match):
        before, notextile, after = match.groups()
        if after == None:
            after = ''
        return ''.join([before, self.shelve(notextile), after])

    def getHTMLComments(self, text):
        """Search the string for HTML comments, e.g. <!-- comment text -->.  We
        send the text that matches this to fParseHTMLComments."""
        return self.doSpecial(text, '<!--', '-->', self.fParseHTMLComments)

    def fParseHTMLComments(self, match):
        """If self.restricted is True, clean the matched contents of the HTML
        comment.  Otherwise, return the comments unchanged.
        The original php had an if statement in here regarding restricted mode.
        nose reported that this line wasn't covered.  It's correct.  In
        restricted mode, the html comment tags have already been converted to
        &lt;!*#8212; and &#8212;&gt; so they don't match in getHTMLComments,
        and never arrive here.
        """
        before, commenttext, after = match.groups()
        commenttext = self.shelve(commenttext)
        return '<!--%s-->' % commenttext

    def redcloth_list(self, text):
        """Parse the text for definition lists and send them to be
        formatted."""
        pattern = re.compile(r"^([-]+%s[ .].*:=.*)$(?![^-])" % self.lc, re.M
                | re.U | re.S)
        return pattern.sub(self.fRCList, text)

    def fRCList(self, match):
        """Format a definition list."""
        out = []
        text = re.split(r'\n(?=[-])', match.group(), flags=re.M)
        for line in text:
            # parse the attributes and content
            m = re.match(r'^[-]+(%s)[ .](.*)$' % self.lc, line, re.M | re.S)

            atts, content = m.groups()
            # cleanup
            content = content.strip()
            atts = self.pba(atts)

            # split the content into the term and definition
            xm = re.match(r'^(.*?)[\s]*:=(.*?)[\s]*(=:|:=)?[\s]*$', content,
                    re.S)
            term, definition, ending = xm.groups()
            # cleanup
            term = term.strip()
            definition = definition.strip(' ')

            # if this is the first time through, out as a bool is False
            if not out:
                if definition == '':
                    dltag = "<dl%s>" % atts
                else:
                    dltag = "<dl>"
                out.append(dltag)

            if definition != '' and term != '':
                if definition.startswith('\n'):
                    definition = '<p>%s</p>' % definition.lstrip()
                definition = definition.replace('\n', '<br />').strip()

                term = self.graf(term)
                definition = self.graf(definition)

                out.extend(['\t<dt%s>%s</dt>' % (atts, term), '\t<dd>%s</dd>'
                    % definition])


        out.append('</dl>')
        out = '\n'.join(out)
        return out

    def placeNoteLists(self, text):
        """Parse the text for endnotes."""
        if self.notes:
            o = OrderedDict()
            for label, info in self.notes.items():
                if 'seq' in info:
                    i = info['seq']
                    info['seq'] = label
                    o[i] = info
                else:
                    self.unreferencedNotes[label] = info

            if o:
                # sort o by key
                o = OrderedDict(sorted(o.items(), key=lambda t: t[0]))
            self.notes = o
        text_re = re.compile('<p>notelist(%s)(?:\:([\w|%s]))?([\^!]?)(\+?)\.?[\s]*</p>'
                % (self.c, self.syms), re.U)
        text = text_re.sub(self.fNoteLists, text)
        return text

    def fNoteLists(self, match):
        """Given the text that matches as a note, format it into HTML."""
        att, start_char, g_links, extras = match.groups()
        start_char = start_char or 'a'
        index = '%s%s%s' % (g_links, extras, start_char)
        result = ''

        if index not in self.notelist_cache:
            o = []
            if self.notes:
                for seq, info in self.notes.items():
                    links = self.makeBackrefLink(info, g_links, start_char)
                    atts = ''
                    if 'def' in info:
                        infoid = info['id']
                        atts = info['def']['atts']
                        content = info['def']['content']
                        li = """\t<li%s>%s<span id="note%s"> </span>%s</li>""" % (atts, links, infoid, content)
                    else:
                        li = """\t<li%s>%s Undefined Note [#%s].<li>""" % (atts, links, info['seq'])
                    o.append(li)
            if '+' == extras and self.unreferencedNotes:
                for seq, info in self.unreferencedNotes.items():
                    if info['def']:
                        atts = info['def']['atts']
                        content = info['def']['content']
                        li = """\t<li%s>%s</li>""" % (atts, content)
                    o.append(li)
            self.notelist_cache[index] = u"\n".join(o)
            result = self.notelist_cache[index]
        if result:
            list_atts = self.pba(att)
            result = """<ol%s>\n%s\n</ol>""" % (list_atts, result)
        return result

    def makeBackrefLink(self, info, g_links, i):
        """Given the pieces of a back reference link, create an <a> tag."""
        atts, content, infoid, link = '', '', '', ''
        if 'def' in info:
            link = info['def']['link']
        backlink_type = link or g_links
        i_ = self.encode_high(i)
        allow_inc = i not in self.syms
        i_ = int(i_)

        if backlink_type == "!":
            return ''
        elif backlink_type == '^':
            return """<sup><a href="#noteref%s">%s</a></sup>""" % (info['refids'][0], i)
        else:
            result = []
            for refid in info['refids']:
                i_entity = self.decode_high(i_)
                sup = """<sup><a href="#noteref%s">%s</a></sup>""" % (refid, i_entity)
                if allow_inc:
                    i_ += 1
                result.append(sup)
            result = ' '.join(result)
            return result

    def fParseNoteDefs(self, m):
        """Parse the note definitions and format them as HTML"""
        label, link, att, content = m.groups()

        # Assign an id if the note reference parse hasn't found the label yet.
        if label not in self.notes:
            self.notes[label] = {'id': str(uuid.uuid4()).replace('-', '')}

        # Ignores subsequent defs using the same label
        if 'def' not in self.notes[label]:
            self.notes[label]['def'] = {'atts': self.pba(att), 'content':
                    self.graf(content), 'link': link}
        return ''

    def noteRef(self, text):
        """Search the text looking for note references."""
        text_re = re.compile(r"""
        \[          # start
        (%s)        # !atts
        \#
        ([^\]!]+)  # !label
        ([!]?)      # !nolink
        \]""" % self.c, re.X)
        text = text_re.sub(self.fParseNoteRefs, text)
        return text

    def fParseNoteRefs(self, match):
        """Parse and format the matched text into note references.
        By the time this function is called, all the defs will have been
        processed into the notes array. So now we can resolve the link numbers
        in the order we process the refs..."""
        atts, label, nolink = match.groups()
        atts = self.pba(atts)
        nolink = nolink == '!'

        # Assign a sequence number to this reference if there isn't one already
        if label in self.notes:
            num = self.notes[label]['seq']
        else:
            self.notes[label] = {'seq': self.note_index, 'refids': [], 'id': ''}
            num = self.note_index
            self.note_index += 1

        # Make our anchor point and stash it for possible use in backlinks when
        # the note list is generated later...
        refid = str(uuid.uuid4()).replace('-', '')
        self.notes[label]['refids'].append(refid)

        # If we are referencing a note that hasn't had the definition parsed
        # yet, then assign it an ID...
        if not self.notes[label]['id']:
            self.notes[label]['id'] = str(uuid.uuid4()).replace('-', '')
        labelid = self.notes[label]['id']

        # Build the link (if any)...
        result = '<span id="noteref%s">%s</span>' % (refid, num)
        if not nolink:
            result = """<a href="#note%s">%s</a>""" % (labelid, result)

        # Build the reference...
        result = '<sup%s>%s</sup>' % (atts, result)
        return result

    def encode_high(self, text):
        """Encode the text so that it is an appropriate HTML entity."""
        return ord(text)

    def decode_high(self, text):
        """Decode encoded HTML entities."""
        h = HTMLParser()
        text = '&#%s;' % text
        return h.unescape(text)


def textile(text, head_offset=0, html_type='xhtml', auto_link=False,
            encoding=None, output=None):
    """
    Apply Textile to a block of text.

    This function takes the following additional parameters:

    auto_link - enable automatic linking of URLs (default: False)
    head_offset - offset to apply to heading levels (default: 0)
    html_type - 'xhtml' or 'html' style tags (default: 'xhtml')

    """
    return Textile(auto_link=auto_link).textile(text, head_offset=head_offset,
                                                  html_type=html_type)


def textile_restricted(text, lite=True, noimage=True, html_type='xhtml',
                       auto_link=False):
    """
    Apply Textile to a block of text, with restrictions designed for weblog
    comments and other untrusted input.  Raw HTML is escaped, style attributes
    are disabled, and rel='nofollow' is added to external links.

    This function takes the following additional parameters:

    auto_link - enable automatic linking of URLs (default: False)
    html_type - 'xhtml' or 'html' style tags (default: 'xhtml')
    lite - restrict block tags to p, bq, and bc, disable tables (default: True)
    noimage - disable image tags (default: True)

    """
    return Textile(restricted=True, lite=lite,
                   noimage=noimage, auto_link=auto_link).textile(
        text, rel='nofollow', html_type=html_type)
