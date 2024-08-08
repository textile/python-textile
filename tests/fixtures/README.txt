	<p><a href="https://github.com/textile/python-textile/actions/workflows/lint_and_test.yml"><img alt="python-textile" src="https://github.com/textile/python-textile/actions/workflows/lint_and_test.yml/badge.svg" title="python-textile" /></a> <a href="https://codecov.io/github/textile/python-textile"><img alt="" src="https://codecov.io/github/textile/python-textile/coverage.svg" /></a> <img alt="" src="https://img.shields.io/pypi/pyversions/textile" /> <img alt="" src="https://img.shields.io/pypi/wheel/textile" /></p>

	<h1>python-textile</h1>

	<p>python-textile is a Python port of <a href="http://txstyle.org/">Textile</a>, Dean Allen&#8217;s humane web text generator.</p>

	<h2>Installation</h2>

	<p><code>pip install textile</code></p>

	<p>Dependencies:
	<ul>
		<li><a href="https://pypi.org/project/html5lib/">html5lib</a></li>
		<li><a href="https://pypi.org/project/regex/">regex</a> (The regex package causes problems with PyPy, and is not installed as a dependency in such environments. If you are upgrading a textile install on PyPy which had regex previously included, you may need to uninstall it.)</li>
	</ul></p>

	<p>Optional dependencies include:
	<ul>
		<li><a href="http://python-pillow.github.io/"><span class="caps">PIL</span>/Pillow</a> (for checking image sizes). If needed, install via <code>pip install 'textile[imagesize]'</code></li>
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
		<li>Active development supports Python 3.8 or later.</li>
	</ul>

	<h3>Running Tests</h3>

	<p>To run the test suite, use pytest. `pytest-cov` is required as well.</p>

	<p>When textile is installed locally:</p>

<pre><code>pytest

When textile is not installed locally:</code></pre>

<pre><code>PYTHONPATH=. pytest</code></pre>