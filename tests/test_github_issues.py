# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import textile

def test_github_issue_16():
    result = textile.textile('"$":http://google.com "$":https://google.com "$":mailto:blackhole@sun.comet')
    expect = '\t<p><a href="http://google.com">google.com</a> <a href="https://google.com">google.com</a> <a href="mailto:blackhole%40sun.comet">blackhole@sun.comet</a></p>'
    assert result == expect

def test_github_issue_17():
    result = textile.textile('!http://www.ox.ac.uk/favicon.ico!')
    expect = '\t<p><img alt="" src="http://www.ox.ac.uk/favicon.ico" /></p>'
    assert result == expect

def test_github_issue_20():
    text = 'This is a link to a ["Wikipedia article about Textile":http://en.wikipedia.org/wiki/Textile_(markup_language)].'
    result = textile.textile(text)
    expect = '\t<p>This is a link to a <a href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Wikipedia article about Textile</a>.</p>'
    assert result == expect

def test_github_issue_21():
    text = '''h1. xml example

bc. 
<foo>
  bar
</foo>'''
    result = textile.textile(text)
    expect = '\t<h1>xml example</h1>\n\n<pre><code>\n&lt;foo&gt;\n  bar\n&lt;/foo&gt;\n</code></pre>'
    assert result == expect

def test_github_issue_22():
    text = '''_(artist-name)Ty Segall_’s'''
    result = textile.textile(text)
    expect = '\t<p><em class="artist-name">Ty Segall</em>’s</p>'
    assert result == expect

def test_github_issue_26():
    text = ''
    result = textile.textile(text)
    expect = ''
    assert result == expect

def test_github_issue_27():
    test = """* Folders with ":" in their names are displayed with a forward slash "/" instead. (Filed as "#4581709":/test/link, which was considered "normal behaviour" - quote: "Please note that Finder presents the 'Carbon filesystem' view, regardless of the underlying filesystem.")"""
    result = textile.textile(test)
    expect = """\t<ul>\n\t\t<li>Folders with &#8220;:&#8221; in their names are displayed with a forward slash &#8220;/&#8221; instead. (Filed as <a href="/test/link">#4581709</a>, which was considered &#8220;normal behaviour&#8221; &#8211; quote: &#8220;Please note that Finder presents the &#8216;Carbon filesystem&#8217; view, regardless of the underlying filesystem.&#8221;)</li>\n\t</ul>"""
    assert result == expect

def test_github_issue_28():
    test = """So here I am porting my ancient "newspipe":newspipe "front-end":blog/2006/09/30/0950 to "Snakelets":Snakelets and "Python":Python, and I've just trimmed down over 20 lines of "PHP":PHP down to essentially one line of "BeautifulSoup":BeautifulSoup retrieval:

<pre>
def parseWapProfile(self, url):
  result = fetch.fetchURL(url)
  soup = BeautifulStoneSoup(result['data'], convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
  try:
    width, height = soup('prf:screensize')[0].contents[0].split('x')
  except:
    width = height = None
  return {"width": width, "height": height}
</pre>

Of course there's a lot more error handling to do (and useful data to glean off the "XML":XML), but being able to cut through all the usual parsing crap is immensely gratifying."""
    result = textile.textile(test)
    expect = ("""\t<p>So here I am porting my ancient <a href="newspipe">newspipe</a> <a href="blog/2006/09/30/0950">front-end</a> to <a href="Snakelets">Snakelets</a> and <a href="Python">Python</a>, and I&#8217;ve just trimmed down over 20 lines of <a href="PHP"><span class="caps">PHP</span></a> down to essentially one line of <a href="BeautifulSoup">BeautifulSoup</a> retrieval:</p>

<pre>
def parseWapProfile(self, url):
  result = fetch.fetchURL(url)
  soup = BeautifulStoneSoup(result[&#39;data&#39;], convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
  try:
    width, height = soup(&#39;prf:screensize&#39;)[0].contents[0].split(&#39;x&#39;)
  except:
    width = height = None
  return {&quot;width&quot;: width, &quot;height&quot;: height}
</pre>

\t<p>Of course there&#8217;s a lot more error handling to do (and useful data to glean off the <a href="XML"><span class="caps">XML</span></a>), but being able to cut through all the usual parsing crap is immensely gratifying.</p>""")
    assert result == expect

def test_github_issue_30():
    text ='"Tëxtíle (Tëxtíle)":http://lala.com'
    result = textile.textile(text)
    expect = '\t<p><a href="http://lala.com" title="Tëxtíle">Tëxtíle</a></p>'
    assert result == expect

def test_github_issue_36():
    text = '"Chögyam Trungpa":https://www.google.com/search?q=Chögyam+Trungpa'
    result = textile.textile(text)
    expect = '\t<p><a href="https://www.google.com/search?q=Chögyam+Trungpa">Chögyam Trungpa</a></p>'
    assert result == expect

def test_github_issue_37():
    text = '* xxx\n* yyy\n*blah*\n* test'
    result = textile.textile(text)
    expect = '\t<ul>\n\t\t<li>xxx</li>\n\t\t<li>yyy<br />\n<strong>blah</strong></li>\n\t\t<li>test</li>\n\t</ul>'
    assert result == expect

def test_github_issue_40():
    text = '\r\n'
    result = textile.textile(text)
    expect = '\r\n'
    assert result == expect
