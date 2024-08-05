# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import re
import textile


def test_FootnoteReference():
    html = textile.textile('YACC[1]')
    assert re.search(r'^\t<p><span class="caps">YACC</span><sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">1</a></sup></p>', html) is not None


def test_Footnote():
    html = textile.textile('This is covered elsewhere[1].\n\nfn1. Down here, in fact.\n\nfn2. Here is another footnote.')
    assert re.search(r'^\t<p>This is covered elsewhere<sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">1</a></sup>.</p>\n\n\t<p class="footnote" id="fn\1-1"><sup>1</sup> Down here, in fact.</p>\n\n\t<p class="footnote" id="fn\1-2"><sup>2</sup> Here is another footnote.</p>$', html) is not None

    html = textile.textile('''See[1] for details -- or perhaps[100] at a push.\n\nfn1. Here are the details.\n\nfn100(footy#otherid). A totally unrelated footnote.''')
    assert re.search(r'^\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">1</a></sup> for details &#8212; or perhaps<sup class="footnote" id="fnrev\1-2"><a href="#fn\1-2">100</a></sup> at a push.</p>\n\n\t<p class="footnote" id="fn\1-1"><sup>1</sup> Here are the details.</p>\n\n\t<p class="footy" id="otherid"><sup id="fn\1-2">100</sup> A totally unrelated footnote.</p>$', html) is not None

    html = textile.textile('''See[2] for details, and later, reference it again[2].\n\nfn2^(footy#otherid)[en]. Here are the details.''')
    assert re.search(r'^\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">2</a></sup> for details, and later, reference it again<sup class="footnote"><a href="#fn\1-1">2</a></sup>.</p>\n\n\t<p class="footy" id="otherid" lang="en"><sup id="fn\1-1"><a href="#fnrev\1-1">2</a></sup> Here are the details.</p>$', html) is not None

    html = textile.textile('''See[3!] for details.\n\nfn3. Here are the details.''')
    assert re.search(r'^\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1">3</sup> for details.</p>\n\n\t<p class="footnote" id="fn\1-1"><sup>3</sup> Here are the details.</p>$', html) is not None

    html = textile.textile('''See[4!] for details.\n\nfn4^. Here are the details.''')
    assert re.search(r'^\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1">4</sup> for details.</p>\n\n\t<p class="footnote" id="fn\1-1"><sup><a href="#fnrev\1-1">4</a></sup> Here are the details.</p>$', html) is not None


def test_issue_35():
    result = textile.textile('"z"')
    expect = '\t<p>&#8220;z&#8221;</p>'
    assert result == expect

    result = textile.textile('" z"')
    expect = '\t<p>&#8220; z&#8221;</p>'
    assert result == expect


def test_restricted():
    # Note that the HTML is escaped, thus rendering the <script> tag harmless.
    test = "Here is some text.\n<script>alert('hello world')</script>"
    result = textile.textile_restricted(test)
    expect = "\t<p>Here is some text.<br />\n&lt;script&gt;alert(&#8216;hello world&#8217;)&lt;/script&gt;</p>"

    assert result == expect

    test = "Here's some <!-- commented *out* --> text."
    result = textile.textile_restricted(test)
    expect = "\t<p>Here&#8217;s some &lt;!&#8212; commented <strong>out</strong> &#8212;&gt; text.</p>"

    assert result == expect

    test = "p[fr]. Partir, c'est toujours mourir un peu."
    result = textile.textile_restricted(test)
    expect = '\t<p lang="fr">Partir, c&#8217;est toujours mourir un peu.</p>'

    assert result == expect

    test = "p{color:blue}. is this blue?"
    result = textile.textile_restricted(test)
    expect = '\t<p>is this blue?</p>'

    assert result == expect

    test = """\
table{border:1px solid black}.
|={color:gray}. Your caption goes here
|~.
|{position:absolute}. A footer | foo |
|-.
|_{font-size:xxlarge}. header|_=. centered header|
|~. bottom aligned|{background:red;width:200px}. asfd|"""
    result = textile.textile_restricted(test, lite=False)
    # styles from alignment hints like =. and ~. are ok
    expect = '''\
\t<table>
\t<caption>Your caption goes here</caption>

\t<tfoot>
\t\t<tr>
\t\t\t<td>A footer </td>
\t\t\t<td> foo </td>
\t\t</tr>
\t</tfoot>
\t<tbody>
\t\t<tr>
\t\t\t<th>header</th>
\t\t\t<th style="text-align:center;">centered header</th>
\t\t</tr>
\t\t<tr>
\t\t\t<td style="vertical-align:bottom;">bottom aligned</td>
\t\t\t<td>asfd</td>
\t\t</tr>
\t</tbody>
\t</table>'''

    assert result == expect


def test_unicode_footnote():
    html = textile.textile('текст[1]')
    assert re.compile(r'^\t<p>текст<sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">1</a></sup></p>$', re.U).search(html) is not None


def test_autolinking():
    test = """some text "test":http://www.google.com http://www.google.com "$":http://www.google.com"""
    result = """\t<p>some text <a href="http://www.google.com">test</a> http://www.google.com <a href="http://www.google.com">www.google.com</a></p>"""
    expect = textile.textile(test)

    assert result == expect


def test_sanitize():
    test = "a paragraph of benign text"
    result = "\t<p>a paragraph of benign text</p>"
    expect = textile.Textile().parse(test, sanitize=True)
    assert result == expect

    test = """<p style="width: expression(alert('evil'));">a paragraph of evil text</p>"""
    result = '<p style="">a paragraph of evil text</p>'
    expect = textile.Textile().parse(test, sanitize=True)
    assert result == expect

    test = """<p>a paragraph of benign text<br />and more text</p>"""
    result = '<p>a paragraph of benign text<br />\nand more text</p>'
    expect = textile.Textile(html_type='html5').parse(test, sanitize=True)
    assert result == expect


def test_imagesize():
    PIL = pytest.importorskip('PIL')  # noqa: F841

    test = "!http://www.google.com/intl/en_ALL/images/srpr/logo1w.png!"
    result = '\t<p><img alt="" height="95" src="http://www.google.com/intl/en_ALL/images/srpr/logo1w.png" width="275" /></p>'
    expect = textile.Textile(get_sizes=True).parse(test)
    assert result == expect


def test_endnotes_simple():
    test = """Scientists say the moon is slowly shrinking[#my_first_label].\n\nnotelist!.\n\nnote#my_first_label Over the past billion years, about a quarter of the moon's 4.5 billion-year lifespan, it has shrunk about 200 meters (700 feet) in diameter."""
    html = textile.textile(test)
    result_pattern = r"""\t<p>Scientists say the moon is slowly shrinking<sup><a href="#note([a-f0-9]{32})-2"><span id="noteref\1-1">1</span></a></sup>.</p>\n\n\t<ol>\n\t\t<li><span id="note\1-2"> </span>Over the past billion years, about a quarter of the moon&#8217;s 4.5 billion-year lifespan, it has shrunk about 200 meters \(700 feet\) in diameter.</li>\n\t</ol>$"""
    result_re = re.compile(result_pattern)
    assert result_re.search(html) is not None


def test_endnotes_complex():
    test = """Tim Berners-Lee is one of the pioneer voices in favour of Net Neutrality[#netneutral] and has expressed the view that ISPs should supply "connectivity with no strings attached"[#netneutral!] [#tbl_quote]\n\nBerners-Lee admitted that the forward slashes ("//") in a web address were actually unnecessary.  He told the newspaper that he could easily have designed URLs not to have the forward slashes.  "... it seemed like a good idea at the time,"[#slashes]\n\nnote#netneutral. "Web creator rejects net tracking":http://news.bbc.co.uk/2/hi/technology/7613201.stm. BBC. 15 September 2008\n\nnote#tbl_quote. "Web inventor's warning on spy software":http://www.telegraph.co.uk/news/uknews/1581938/Web-inventor%27s-warning-on-spy-software.html. The Daily Telegraph (London). 25 May 2008\n\nnote#slashes. "Berners-Lee 'sorry' for slashes":http://news.bbc.co.uk/1/hi/technology/8306631.stm. BBC. 14 October 2009\n\nnotelist."""
    html = textile.textile(test)
    result_pattern = r"""\t<p>Tim Berners-Lee is one of the pioneer voices in favour of Net Neutrality<sup><a href="#note([a-f0-9]{32})-2"><span id="noteref\1-1">1</span></a></sup> and has expressed the view that <span class="caps">ISP</span>s should supply &#8220;connectivity with no strings attached&#8221;<sup><span id="noteref\1-3">1</span></sup> <sup><a href="#note\1-5"><span id="noteref\1-4">2</span></a></sup></p>\n\n\t<p>Berners-Lee admitted that the forward slashes \(&#8220;//&#8221;\) in a web address were actually unnecessary.  He told the newspaper that he could easily have designed <span class="caps">URL</span>s not to have the forward slashes.  &#8220;&#8230; it seemed like a good idea at the time,&#8221;<sup><a href="#note\1-7"><span id="noteref\1-6">3</span></a></sup></p>\n\n\t<ol>\n\t\t<li><sup><a href="#noteref\1-1">a</a></sup> <sup><a href="#noteref\1-3">b</a></sup><span id="note\1-2"> </span><a href="http://news.bbc.co.uk/2/hi/technology/7613201.stm">Web creator rejects net tracking</a>. <span class="caps">BBC</span>. 15 September 2008</li>\n\t\t<li><sup><a href="#noteref\1-4">a</a></sup><span id="note\1-5"> </span><a href="http://www.telegraph.co.uk/news/uknews/1581938/Web-inventor%27s-warning-on-spy-software.html">Web inventor&#8217;s warning on spy software</a>. The Daily Telegraph \(London\). 25 May 2008</li>\n\t\t<li><sup><a href="#noteref\1-6">a</a></sup><span id="note\1-7"> </span><a href="http://news.bbc.co.uk/1/hi/technology/8306631.stm">Berners-Lee &#8216;sorry&#8217; for slashes</a>. <span class="caps">BBC</span>. 14 October 2009</li>\n\t</ol>$"""
    result_re = re.compile(result_pattern)
    assert result_re.search(html) is not None


def test_endnotes_unreferenced_note():
    test = """Scientists say[#lavader] the moon is quite small. But I, for one, don't believe them. Others claim it to be made of cheese[#aardman]. If this proves true I suspect we are in for troubled times[#apollo13] as people argue over their "share" of the moon's cheese. In the end, its limited size[#lavader] may prove problematic.\n\nnote#lavader(noteclass). "Proof of the small moon hypothesis":http://antwrp.gsfc.nasa.gov/apod/ap080801.html. Copyright(c) Laurent Laveder\n\nnote#aardman(#noteid). "Proof of a cheese moon":http://www.imdb.com/title/tt0104361\n\nnote#apollo13. After all, things do go "wrong":http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident.\n\nnotelist{padding:1em; margin:1em; border-bottom:1px solid gray}.\n\nnotelist{padding:1em; margin:1em; border-bottom:1px solid gray}:§^.\n\nnotelist{padding:1em; margin:1em; border-bottom:1px solid gray}:‡"""
    html = textile.textile(test)
    result_pattern = r"""\t<p>Scientists say<sup><a href="#note([a-f0-9]{32})-2"><span id="noteref\1-1">1</span></a></sup> the moon is quite small. But I, for one, don&#8217;t believe them. Others claim it to be made of cheese<sup><a href="#note\1-4"><span id="noteref\1-3">2</span></a></sup>. If this proves true I suspect we are in for troubled times<sup><a href="#note\1-6"><span id="noteref\1-5">3</span></a></sup> as people argue over their &#8220;share&#8221; of the moon&#8217;s cheese. In the end, its limited size<sup><a href="#note\1-2"><span id="noteref\1-7">1</span></a></sup> may prove problematic.</p>\n\n\t<ol style="padding:1em; margin:1em; border-bottom:1px solid gray;">\n\t\t<li class="noteclass"><sup><a href="#noteref\1-1">a</a></sup> <sup><a href="#noteref\1-7">b</a></sup><span id="note\1-2"> </span><a href="http://antwrp.gsfc.nasa.gov/apod/ap080801.html">Proof of the small moon hypothesis</a>. Copyright&#169; Laurent Laveder</li>\n\t\t<li id="noteid"><sup><a href="#noteref\1-3">a</a></sup><span id="note\1-4"> </span><a href="http://www.imdb.com/title/tt0104361">Proof of a cheese moon</a></li>\n\t\t<li><sup><a href="#noteref\1-5">a</a></sup><span id="note\1-6"> </span>After all, things do go <a href="http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident">wrong</a>.</li>\n\t</ol>\n\n\t<ol style="padding:1em; margin:1em; border-bottom:1px solid gray;">\n\t\t<li class="noteclass"><sup><a href="#noteref\1-1">§</a></sup><span id="note\1-2"> </span><a href="http://antwrp.gsfc.nasa.gov/apod/ap080801.html">Proof of the small moon hypothesis</a>. Copyright&#169; Laurent Laveder</li>\n\t\t<li id="noteid"><sup><a href="#noteref\1-3">§</a></sup><span id="note\1-4"> </span><a href="http://www.imdb.com/title/tt0104361">Proof of a cheese moon</a></li>\n\t\t<li><sup><a href="#noteref\1-5">§</a></sup><span id="note\1-6"> </span>After all, things do go <a href="http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident">wrong</a>.</li>\n\t</ol>\n\n\t<ol style="padding:1em; margin:1em; border-bottom:1px solid gray;">\n\t\t<li class="noteclass"><sup><a href="#noteref\1-1">‡</a></sup> <sup><a href="#noteref\1-7">‡</a></sup><span id="note\1-2"> </span><a href="http://antwrp.gsfc.nasa.gov/apod/ap080801.html">Proof of the small moon hypothesis</a>. Copyright&#169; Laurent Laveder</li>\n\t\t<li id="noteid"><sup><a href="#noteref\1-3">‡</a></sup><span id="note\1-4"> </span><a href="http://www.imdb.com/title/tt0104361">Proof of a cheese moon</a></li>\n\t\t<li><sup><a href="#noteref\1-5">‡</a></sup><span id="note\1-6"> </span>After all, things do go <a href="http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident">wrong</a>.</li>\n\t</ol>"""
    result_re = re.compile(result_pattern, re.U)
    assert result_re.search(html) is not None


def test_endnotes_malformed():
    test = """Scientists say[#lavader] the moon is quite small. But I, for one, don't believe them. Others claim it to be made of cheese[#aardman]. If this proves true I suspect we are in for troubled times[#apollo13!] as people argue over their "share" of the moon's cheese. In the end, its limited size[#lavader] may prove problematic.\n\nnote#unused An unreferenced note.\n\nnote#lavader^ "Proof of the small moon hypothesis":http://antwrp.gsfc.nasa.gov/apod/ap080801.html. Copyright(c) Laurent Laveder\n\nnote#aardman^ "Proof of a cheese moon":http://www.imdb.com/title/tt0104361\n\nnote#apollo13^ After all, things do go "wrong":http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident.\n\nnotelist{padding:1em; margin:1em; border-bottom:1px solid gray}:α!+"""
    html = textile.textile(test)
    result_pattern = r"""^\t<p>Scientists say<sup><a href="#note([a-f0-9]{32})-2"><span id="noteref\1-1">1</span></a></sup> the moon is quite small. But I, for one, don&#8217;t believe them. Others claim it to be made of cheese<sup><a href="#note\1-4"><span id="noteref\1-3">2</span></a></sup>. If this proves true I suspect we are in for troubled times<sup><span id="noteref\1-5">3</span></sup> as people argue over their &#8220;share&#8221; of the moon&#8217;s cheese. In the end, its limited size<sup><a href="#note\1-2"><span id="noteref\1-7">1</span></a></sup> may prove problematic.</p>\n\n\t<ol style="padding:1em; margin:1em; border-bottom:1px solid gray;">\n\t\t<li><sup><a href="#noteref\1-1">α</a></sup><span id="note\1-2"> </span><a href="http://antwrp.gsfc.nasa.gov/apod/ap080801.html">Proof of the small moon hypothesis</a>. Copyright&#169; Laurent Laveder</li>\n\t\t<li><sup><a href="#noteref\1-3">α</a></sup><span id="note\1-4"> </span><a href="http://www.imdb.com/title/tt0104361">Proof of a cheese moon</a></li>\n\t\t<li><sup><a href="#noteref\1-5">α</a></sup><span id="note\1-6"> </span>After all, things do go <a href="http://en.wikipedia.org/wiki/Apollo_13#The_oxygen_tank_incident">wrong</a>.</li>\n\t\t<li>An unreferenced note.</li>\n\t</ol>$"""
    result_re = re.compile(result_pattern, re.U)
    assert result_re.search(html) is not None


def test_endnotes_undefined_note():
    test = """Scientists say the moon is slowly shrinking[#my_first_label].\n\nnotelist!."""
    html = textile.textile(test)
    result_pattern = r"""\t<p>Scientists say the moon is slowly shrinking<sup><a href="#note([a-f0-9]{32})-2"><span id="noteref\1-1">1</span></a></sup>.</p>\n\n\t<ol>\n\t\t<li> Undefined Note \[#my_first_label\].</li>\n\t</ol>$"""
    result_re = re.compile(result_pattern)
    assert result_re.search(html) is not None


def test_encode_url():
    # I tried adding these as doctests, but the unicode tests weren't
    # returning the correct results.
    t = textile.Textile()

    url = 'http://www.example.local'
    result = 'http://www.example.local'
    eurl = t.encode_url(url)
    assert eurl == result

    url = 'http://user@www.example.local'
    result = 'http://user@www.example.local'
    eurl = t.encode_url(url)
    assert eurl == result

    url = 'http://user:password@www.example.local'
    result = 'http://user:password@www.example.local'
    eurl = t.encode_url(url)
    assert eurl == result

    url = 'http://user:password@www.example.local/Ubermensch'
    result = 'http://user:password@www.example.local/Ubermensch'
    eurl = t.encode_url(url)
    assert eurl == result

    url = "http://user:password@www.example.local/Übermensch"
    result = "http://user:password@www.example.local/%C3%9Cbermensch"
    eurl = t.encode_url(url)
    assert eurl == result

    url = 'http://user:password@www.example.local:8080/Übermensch'
    result = 'http://user:password@www.example.local:8080/%C3%9Cbermensch'
    eurl = t.encode_url(url)
    assert eurl == result


def test_footnote_crosslink():
    html = textile.textile('''See[2] for details, and later, reference it again[2].\n\nfn2^(footy#otherid)[en]. Here are the details.''')
    searchstring = r'\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">2</a></sup> for details, and later, reference it again<sup class="footnote"><a href="#fn\1-1">2</a></sup>.</p>\n\n\t<p class="footy" id="otherid" lang="en"><sup id="fn\1-1"><a href="#fnrev\1-1">2</a></sup> Here are the details.</p>$'
    assert re.compile(searchstring).search(html) is not None


def test_footnote_without_reflink():
    html = textile.textile('''See[3!] for details.\n\nfn3. Here are the details.''')
    searchstring = r'^\t<p>See<sup class="footnote" id="fnrev([a-f0-9]{32})-1">3</sup> for details.</p>\n\n\t<p class="footnote" id="fn\1-1"><sup>3</sup> Here are the details.</p>$'
    assert re.compile(searchstring).search(html) is not None


def testSquareBrackets():
    html = textile.textile("""1[^st^], 2[^nd^], 3[^rd^]. 2 log[~n~]\n\nA close[!http://textpattern.com/favicon.ico!]image.\nA tight["text":http://textpattern.com/]link.\nA ["footnoted link":http://textpattern.com/][182].""")
    searchstring = r'^\t<p>1<sup>st</sup>, 2<sup>nd</sup>, 3<sup>rd</sup>. 2 log<sub>n</sub></p>\n\n\t<p>A close<img alt="" src="http://textpattern.com/favicon.ico" />image.<br />\nA tight<a href="http://textpattern.com/">text</a>link.<br />\nA <a href="http://textpattern.com/">footnoted link</a><sup class="footnote" id="fnrev([a-f0-9]{32})-1"><a href="#fn\1-1">182</a></sup>.</p>'
    assert re.compile(searchstring).search(html) is not None


def test_html5():
    """docstring for testHTML5"""

    test = 'We use CSS(Cascading Style Sheets).'
    result = '\t<p>We use <abbr title="Cascading Style Sheets"><span class="caps">CSS</span></abbr>.</p>'
    expect = textile.textile(test, html_type="html5")
    assert result == expect


def test_relURL():
    t = textile.Textile()
    t.restricted = True
    assert t.relURL("gopher://gopher.com/") == '#'
