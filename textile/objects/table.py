# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
from xml.etree import ElementTree

from textile.regex_strings import (align_re_s, cls_re_s, regex_snippets,
        table_span_re_s, valign_re_s)
from textile.utils import encode_html, generate_tag, parse_attributes

try:
    import regex as re
except ImportError:
    import re


class Table(object):
    def __init__(self, textile, tatts, rows, summary):
        self.textile = textile
        self.attributes = parse_attributes(tatts, 'table')
        if summary:
            self.attributes.update(summary=summary.strip())
        self.input = rows
        self.caption = ''
        self.colgroup = ''
        self.content = []

    def process(self):
        rgrp = None
        groups = []
        if self.input[-1] == '|': # pragma: no branch
            self.input = '{0}\n'.format(self.input)
        split = self.input.split('|\n')
        for i, row in enumerate([x for x in split if x]):
            row = row.lstrip()

            # Caption -- only occurs on row 1, otherwise treat '|=. foo |...'
            # as a normal center-aligned cell.
            if i == 0 and row[:2] == '|=':
                captionpattern = (r"^\|\=(?P<capts>{s}{a}{c})\. "
                                  r"(?P<cap>[^\n]*)(?P<row>.*)".format(**{
                                      's': table_span_re_s, 'a': align_re_s,
                                      'c': cls_re_s}))
                caption_re = re.compile(captionpattern, re.S)
                cmtch = caption_re.match(row)
                if cmtch:
                    caption = Caption(**cmtch.groupdict())
                    self.caption = '\n{0}'.format(caption.caption)
                    row = cmtch.group('row').lstrip()
                    if row == '':
                        continue

            # Colgroup -- A colgroup row will not necessarily end with a |.
            # Hence it may include the next row of actual table data.
            if row[:2] == '|:':
                if '\n' in row:
                    colgroup_data, row = row[2:].split('\n')
                else:
                    colgroup_data, row = row[2:], ''
                colgroup_atts, cols = colgroup_data, None
                if '|' in colgroup_data:
                    colgroup_atts, cols = colgroup_data.split('|', 1)
                colgrp = Colgroup(cols, colgroup_atts)
                self.colgroup = colgrp.process()
                if row == '':
                    continue

            # search the row for a table group - thead, tfoot, or tbody
            grpmatchpattern = (r"(:?^\|(?P<part>{v})(?P<rgrpatts>{s}{a}{c})"
                    r"\.\s*$\n)?^(?P<row>.*)").format(**{'v': valign_re_s, 's':
                        table_span_re_s, 'a': align_re_s, 'c': cls_re_s})
            grpmatch_re = re.compile(grpmatchpattern, re.S | re.M)
            grpmatch = grpmatch_re.match(row.lstrip())

            grptypes = {'^': Thead, '~': Tfoot, '-': Tbody}
            if grpmatch.group('part'):
                # we're about to start a new group, so process the current one
                # and add it to the output
                if rgrp:
                    groups.append('\n\t{0}'.format(rgrp.process()))
                rgrp = grptypes[grpmatch.group('part')](grpmatch.group(
                    'rgrpatts'))
            row = grpmatch.group('row')

            rmtch = re.search(r'^(?P<ratts>{0}{1}\. )(?P<row>.*)'.format(
                align_re_s, cls_re_s), row.lstrip())
            if rmtch:
                row_atts = parse_attributes(rmtch.group('ratts'), 'tr')
                row = rmtch.group('row')
            else:
                row_atts = {}

            # create a row to hold the cells.
            r = Row(row_atts, row)
            for cellctr, cell in enumerate(row.split('|')[1:]):
                ctag = 'td'
                if cell.startswith('_'):
                    ctag = 'th'

                cmtch = re.search(r'^(?P<catts>_?{0}{1}{2}\. )'
                        '(?P<cell>.*)'.format(table_span_re_s, align_re_s,
                            cls_re_s), cell, flags=re.S)
                if cmtch:
                    catts = cmtch.group('catts')
                    cell_atts = parse_attributes(catts, 'td')
                    cell = cmtch.group('cell')
                else:
                    cell_atts = {}

                if not self.textile.lite:
                    a_pattern = r'(?P<space>{0}*)(?P<cell>.*)'.format(
                            regex_snippets['space'])
                    a = re.search(a_pattern, cell, flags=re.S)
                    cell = self.textile.redcloth_list(a.group('cell'))
                    cell = self.textile.textileLists(cell)
                    cell = '{0}{1}'.format(a.group('space'), cell)

                # create a cell
                c = Cell(ctag, cell, cell_atts)
                cline_tag = '\n\t\t\t{0}'.format(c.process())
                # add the cell to the row
                r.cells.append(self.textile.doTagBr(ctag, cline_tag))

            # if we're in a group, add it to the group's rows, else add it
            # directly to the content
            if rgrp:
                rgrp.rows.append(r.process())
            else:
                self.content.append(r.process())

        # if there's still an rgrp, process it and add it to the output
        if rgrp:
            groups.append('\n\t{0}'.format(rgrp.process()))

        content = '{0}{1}{2}{3}\n\t'.format(self.caption, self.colgroup,
                ''.join(groups), ''.join(self.content))
        tbl = generate_tag('table', content, self.attributes)
        return '\t{0}\n\n'.format(tbl)


class Caption(object):
    def __init__(self, capts, cap, row):
        self.attributes = parse_attributes(capts)
        self.caption = self.process(cap)

    def process(self, cap):
        tag = generate_tag('caption', cap, self.attributes)
        return '\t{0}\n\t'.format(tag)


class Colgroup(object):
    def __init__(self, cols, atts):
        self.row = ''
        self.attributes = atts
        self.cols = cols

    def process(self):
        enc = 'unicode'
        if six.PY2: # pragma: no branch
            enc = 'UTF-8'

        group_atts = parse_attributes(self.attributes, 'col')
        colgroup = ElementTree.Element('colgroup', attrib=group_atts)
        colgroup.text = '\n\t'
        if self.cols is not None:
            has_newline = "\n" in self.cols
            match_cols = self.cols.replace('.', '').split('|')
            # colgroup is the first item in match_cols, the remaining items are
            # cols.
            for idx, col in enumerate(match_cols):
                col_atts = parse_attributes(col.strip(), 'col')
                ElementTree.SubElement(colgroup, 'col', col_atts)
        colgrp = ElementTree.tostring(colgroup, encoding=enc)
        # cleanup the extra xml declaration if it exists, (python versions
        # differ) and then format the resulting string accordingly: newline and
        # tab between cols and a newline at the end
        xml_declaration = "<?xml version='1.0' encoding='UTF-8'?>\n"
        colgrp = colgrp.replace(xml_declaration, '')
        return colgrp.replace('><', '>\n\t<')


class Row(object):
    def __init__(self, attributes, row):
        self.tag = 'tr'
        self.attributes = attributes
        self.cells = []

    def process(self):
        output = []
        for c in self.cells:
            output.append(c)
        cell_data = '{0}\n\t\t'.format(''.join(output))
        tag = generate_tag('tr', cell_data, self.attributes)
        return '\n\t\t{0}'.format(tag)


class Cell(object):
    def __init__(self, tag, content, attributes):
        self.tag = tag
        self.content = content
        self.attributes = attributes

    def process(self):
        return generate_tag(self.tag, self.content, self.attributes)


class _TableSection(object):
    def __init__(self, tag, attributes):
        self.tag = tag
        self.attributes = parse_attributes(attributes)
        self.rows = []

    def process(self):
        return generate_tag(self.tag, '{0}\n\t'.format(''.join(self.rows)), self.attributes)


class Thead(_TableSection):
    def __init__(self, attributes):
        super(Thead, self).__init__('thead', attributes)


class Tbody(_TableSection):
    def __init__(self, attributes):
        super(Tbody, self).__init__('tbody', attributes)


class Tfoot(_TableSection):
    def __init__(self, attributes):
        super(Tfoot, self).__init__('tfoot', attributes)
