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