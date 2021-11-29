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
    text = ('''h1. xml example

bc. '''
            '''
<foo>
  bar
</foo>''')
    result = textile.textile(text)
    expect = '\t<h1>xml example</h1>\n\n<pre><code>\n&lt;foo&gt;\n  bar\n&lt;/foo&gt;</code></pre>'
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
    text = '"Tëxtíle (Tëxtíle)":http://lala.com'
    result = textile.textile(text)
    expect = '\t<p><a href="http://lala.com" title="Tëxtíle">Tëxtíle</a></p>'
    assert result == expect

    text = '!http://lala.com/lol.gif(♡ imáges)!'
    result = textile.textile(text)
    expect = '\t<p><img alt="♡ imáges" src="http://lala.com/lol.gif" title="♡ imáges" /></p>'
    assert result == expect


def test_github_issue_36():
    text = '"Chögyam Trungpa":https://www.google.com/search?q=Chögyam+Trungpa'
    result = textile.textile(text)
    expect = '\t<p><a href="https://www.google.com/search?q=Chögyam+Trungpa">Chögyam Trungpa</a></p>'
    assert result == expect


def test_github_issue_37():
    text = '# xxx\n# yyy\n*blah*'
    result = textile.textile(text)
    expect = '\t<p>\t<ol>\n\t\t<li>xxx</li>\n\t\t<li>yyy</li>\n\t</ol><br />\n<strong>blah</strong></p>'
    assert result == expect

    text = '*Highlights*\n\n* UNITEK Y-3705A Type-C Universal DockingStation Pro\n* USB3.0/RJ45/EARPHONE/MICROPHONE/HDMI 6 PORT HUB 1.2m Data Cable 5V 4A Power Adaptor\n*\n* Dimensions: 25cm x 13cm x 9cm\n* Weight: 0.7kg'
    result = textile.textile(text)
    expect = '''\t<p><strong>Highlights</strong></p>

\t<ul>
\t\t<li><span class="caps">UNITEK</span> Y-3705A Type-C Universal DockingStation Pro</li>
\t\t<li>USB3.0/RJ45/EARPHONE/MICROPHONE/HDMI 6 <span class="caps">PORT</span> <span class="caps">HUB</span> 1.2m Data Cable 5V 4A Power Adaptor</li>
\t</ul>
*
\t<ul>
\t\t<li>Dimensions: 25cm x 13cm x 9cm</li>
\t\t<li>Weight: 0.7kg</li>
\t</ul>'''
    assert result == expect


def test_github_issue_40():
    text = '\r\n'
    result = textile.textile(text)
    expect = '\r\n'
    assert result == expect


def test_github_issue_42():
    text = '!./image.png!'
    result = textile.textile(text)
    expect = '\t<p><img alt="" src="./image.png" /></p>'
    assert result == expect


def test_github_issue_43():
    text = 'pre. smart ‘quotes’ are not smart!'
    result = textile.textile(text)
    expect = '<pre>smart ‘quotes’ are not smart!</pre>'
    assert result == expect


def test_github_issue_45():
    """Incorrect transform unicode url"""
    text = '"test":https://myabstractwiki.ru/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'
    result = textile.textile(text)
    expect = '\t<p><a href="https://myabstractwiki.ru/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0">test</a></p>'
    assert result == expect


def test_github_issue_46():
    """Key error on mal-formed numbered lists. CAUTION: both the input and the
    ouput are ugly."""
    text = '# test\n### test\n## test'
    expect = ('\t<ol>\n\t\t<li>test\n\t\t\t<ol>\n\t\t\t\t<li>test</li>'
              '\n\t\t\t</ol></li>\n\t\t<ol>\n\t\t\t<li>test</li>'
              '\n\t\t</ol></li>\n\t\t</ol>')
    result = textile.textile(text)
    assert result == expect


def test_github_issue_47():
    """Incorrect wrap pre-formatted value"""
    text = '''pre.. word

another

word

yet anothe word'''
    result = textile.textile(text)
    expect = '''<pre>word

another

word

yet anothe word</pre>'''
    assert result == expect


def test_github_issue_49():
    """Key error on russian hash-route link"""
    s = '"link":https://ru.vuejs.org/v2/guide/components.html#Входные-параметры'
    result = textile.textile(s)
    expect = '\t<p><a href="https://ru.vuejs.org/v2/guide/components.html#Входные-параметры">link</a></p>'
    assert result == expect


def test_github_issue_50():
    """Incorrect wrap code with Java generics in pre"""
    test = ('pre.. public class Tynopet<T extends Framework> {}\n\nfinal '
            'List<List<String>> multipleList = new ArrayList<>();')
    result = textile.textile(test)
    expect = ('<pre>public class Tynopet&lt;T extends Framework&gt; {}\n\n'
              'final List&lt;List&lt;String&gt;&gt; multipleList = new '
              'ArrayList&lt;&gt;();</pre>')
    assert result == expect


def test_github_issue_51():
    """Link build with $ sign without "http" prefix broken."""
    test = '"$":www.google.com.br'
    result = textile.textile(test)
    expect = '\t<p><a href="www.google.com.br">www.google.com.br</a></p>'
    assert result == expect


def test_github_issue_52():
    """Table build without space after aligment raise a AttributeError."""
    test = '|=.First Header |=. Second Header |'
    result = textile.textile(test)
    expect = ('\t<table>\n\t\t<tr>\n\t\t\t<td>=.First Header '
              '</td>\n\t\t\t<td style="text-align:center;">Second Header </td>'
              '\n\t\t</tr>\n\t</table>')
    assert result == expect


def test_github_issue_55():
    """Incorrect handling of quote entities in extended pre block"""
    test = ('pre.. this is the first line\n\nbut "quotes" in an extended pre '
            'block need to be handled properly.')
    result = textile.textile(test)
    expect = ('<pre>this is the first line\n\nbut &quot;quotes&quot; in an '
              'extended pre block need to be handled properly.</pre>')
    assert result == expect

    # supplied input
    test = ('pre.. import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;'
            '\nimport ru.onyma.job.Context;\nimport ru.onyma.job.'
            'RescheduleTask;\n\nimport java.util.concurrent.'
            'ScheduledExecutorService;\nimport java.util.concurrent.TimeUnit;'
            '\n\n/**\n* @author ustits\n*/\npublic abstract class '
            'MainService<T> extends RescheduleTask implements Context<T> {\n\n'
            'private static final Logger log = LoggerFactory.getLogger('
            'MainService.class);\nprivate final ScheduledExecutorService '
            'scheduler;\n\nprivate boolean isFirstRun = true;\nprivate T '
            'configs;\n\npublic MainService(final ScheduledExecutorService '
            'scheduler) {\nsuper(scheduler);\nthis.scheduler = scheduler;\n}\n'
            '\n@Override\npublic void setConfig(final T configs) {\nthis.'
            'configs = configs;\nif (isFirstRun) {\nscheduler.schedule(this, '
            '0, TimeUnit.SECONDS);\nisFirstRun = false;\n}\n}\n\n@Override\n'
            'public void stop() {\nsuper.stop();\nscheduler.shutdown();\ntry {'
            '\nscheduler.awaitTermination(Long.MAX_VALUE, TimeUnit.DAYS);\n} '
            'catch (InterruptedException ie) {\nlog.warn("Unable to wait for '
            'syncs termination", ie);\nThread.currentThread().interrupt();\n}'
            '\n}\n\nprotected final T getConfigs() {\nreturn configs;\n}\n}')
    result = textile.textile(test)
    expect = ('<pre>import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;'
              '\nimport ru.onyma.job.Context;\nimport ru.onyma.job.'
              'RescheduleTask;\n\nimport java.util.concurrent.'
              'ScheduledExecutorService;\nimport java.util.concurrent.'
              'TimeUnit;\n\n/**\n* @author ustits\n*/\npublic abstract class '
              'MainService&lt;T&gt; extends RescheduleTask implements '
              'Context&lt;T&gt; {\n\nprivate static final Logger log = '
              'LoggerFactory.getLogger(MainService.class);\nprivate final '
              'ScheduledExecutorService scheduler;\n\nprivate boolean '
              'isFirstRun = true;\nprivate T configs;\n\npublic MainService('
              'final ScheduledExecutorService scheduler) {\nsuper(scheduler);'
              '\nthis.scheduler = scheduler;\n}\n\n@Override\npublic void '
              'setConfig(final T configs) {\nthis.configs = configs;\nif ('
              'isFirstRun) {\nscheduler.schedule(this, 0, TimeUnit.SECONDS);'
              '\nisFirstRun = false;\n}\n}\n\n@Override\npublic void stop() {'
              '\nsuper.stop();\nscheduler.shutdown();\ntry {\nscheduler.'
              'awaitTermination(Long.MAX_VALUE, TimeUnit.DAYS);\n} catch '
              '(InterruptedException ie) {\nlog.warn(&quot;Unable to wait '
              'for syncs termination&quot;, ie);\nThread.currentThread().'
              'interrupt();\n}\n}\n\nprotected final T getConfigs() {\n'
              'return configs;\n}\n}</pre>')
    assert result == expect


def test_github_issue_56():
    """Empty description lists throw error"""
    result = textile.textile("- :=\n-")
    expect = '<dl>\n</dl>'
    assert result == expect


def test_github_pull_61():
    """Fixed code block multiline encoding on quotes/span"""
    test = ('''bc.. This is some TEXT inside a "Code BLOCK"

{
  if (JSON) {

    return {"JSON":"value"}
  }
}

Back to 10-4 CAPS '''
            '''

p.. Some multiline Paragragh

Here is some output!!! "Some" CAPS''')

    expect = '''<pre><code>This is some TEXT inside a &quot;Code BLOCK&quot;

{
  if (JSON) {

    return {&quot;JSON&quot;:&quot;value&quot;}
  }
}

Back to 10-4 CAPS </code></pre>

<p>Some multiline Paragragh</p>

<p>Here is some output!!! &#8220;Some&#8221; <span class="caps">CAPS</span></p>'''
    t = textile.Textile()
    result = t.parse(test)
    assert result == expect


def test_github_pull_62():
    """Fix for paragraph multiline, only last paragraph is rendered
    correctly"""
    test = '''p.. First one 'is'

ESCAPED "bad"

p.. Second one 'is'



ESCAPED "bad"

p.. Third one 'is'

ESCAPED "bad"

p.. Last one 'is'

ESCAPED "good" test'''

    expect = '''<p>First one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<p>Second one &#8216;is&#8217;</p>



<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<p>Third one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<p>Last one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;good&#8221; test</p>'''
    t = textile.Textile()
    result = t.parse(test)
    assert result == expect


def test_github_pull_63():
    """Forgot to set multiline_para to False"""
    test = '''p.. First one 'is'

ESCAPED "bad"

bc.. {
 First code BLOCK

 {"JSON":'value'}
}

p.. Second one 'is'



ESCAPED "bad"

p.. Third one 'is'

ESCAPED "bad"

bc.. {
 Last code BLOCK

 {"JSON":'value'}
}

p.. Last one 'is'

ESCAPED "good" test'''

    expect = '''<p>First one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<pre><code>{
 First code BLOCK

 {&quot;JSON&quot;:&#39;value&#39;}
}</code></pre>

<p>Second one &#8216;is&#8217;</p>



<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<p>Third one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;bad&#8221;</p>

<pre><code>{
 Last code BLOCK

 {&quot;JSON&quot;:&#39;value&#39;}
}</code></pre>

<p>Last one &#8216;is&#8217;</p>

<p><span class="caps">ESCAPED</span> &#8220;good&#8221; test</p>'''
    t = textile.Textile()
    result = t.parse(test)
    assert result == expect
