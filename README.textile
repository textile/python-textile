!https://travis-ci.org/textile/python-textile.svg!:https://travis-ci.org/textile/python-textile !https://coveralls.io/repos/github/textile/python-textile/badge.svg!:https://coveralls.io/github/textile/python-textile?branch=master !https://codecov.io/github/textile/python-textile/coverage.svg!:https://codecov.io/github/textile/python-textile

h1. python-textile

python-textile is a Python port of "Textile":http://txstyle.org/, Dean Allen's humane web text generator.

h2. Installation

@pip install textile@

Optional dependencies include:
* "PIL/Pillow":http://python-pillow.github.io/ (for checking images size)
* "regex":https://pypi.python.org/pypi/regex (for faster unicode-aware string matching).

h2. Usage

bc.. import textile
>>> s = """
... _This_ is a *test.*
...
... * One
... * Two
... * Three
...
... Link to "Slashdot":http://slashdot.org/
... """
>>> html = textile.textile(s)
>>> print html
	<p><em>This</em> is a <strong>test.</strong></p>

	<ul>
		<li>One</li>
		<li>Two</li>
		<li>Three</li>
	</ul>

	<p>Link to <a href="http://slashdot.org/">Slashdot</a></p>
>>>

h3. Notes:

* Active development supports Python 2.7 or later (including Python 3.3+).
