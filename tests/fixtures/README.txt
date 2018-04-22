	<p><a href="https://travis-ci.org/textile/python-textile"><img alt="" src="https://travis-ci.org/textile/python-textile.svg" /></a> <a href="https://coveralls.io/github/textile/python-textile?branch=master"><img alt="" src="https://coveralls.io/repos/github/textile/python-textile/badge.svg" /></a> <a href="https://codecov.io/github/textile/python-textile"><img alt="" src="https://codecov.io/github/textile/python-textile/coverage.svg" /></a></p>

	<h1>python-textile</h1>

	<p>python-textile is a Python port of <a href="http://txstyle.org/">Textile</a>, Dean Allen&#8217;s humane web text generator.</p>

	<h2>Installation</h2>

	<p><code>pip install textile</code></p>

	<p>Optional dependencies include:
	<ul>
		<li><a href="http://python-pillow.github.io/"><span class="caps">PIL</span>/Pillow</a> (for checking images size)</li>
		<li><a href="https://pypi.python.org/pypi/regex">regex</a> (for faster unicode-aware string matching).</li>
	</ul></p>

	<h2>Usage</h2>

<pre><code>import textile
&gt;&gt;&gt; s = &quot;&quot;&quot;
... _This_ is a *test.*
...
... * One
... * Two
... * Three
...
... Link to &quot;Slashdot&quot;:http://slashdot.org/
... &quot;&quot;&quot;
&gt;&gt;&gt; html = textile.textile(s)
&gt;&gt;&gt; print html
	&lt;p&gt;&lt;em&gt;This&lt;/em&gt; is a &lt;strong&gt;test.&lt;/strong&gt;&lt;/p&gt;

	&lt;ul&gt;
		&lt;li&gt;One&lt;/li&gt;
		&lt;li&gt;Two&lt;/li&gt;
		&lt;li&gt;Three&lt;/li&gt;
	&lt;/ul&gt;

	&lt;p&gt;Link to &lt;a href=&quot;http://slashdot.org/&quot;&gt;Slashdot&lt;/a&gt;&lt;/p&gt;
&gt;&gt;&gt;</code></pre>

	<h3>Notes:</h3>

	<ul>
		<li>Active development supports Python 2.7 or later (including Python 3.3+).</li>
	</ul>