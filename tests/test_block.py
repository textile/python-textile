import textile
from textile.objects import Block

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def test_block():
    t = textile.Textile()
    result = t.block('h1. foobar baby')
    expect = '\t<h1>foobar baby</h1>'
    assert result == expect

    b = Block(t, "bq", "", None, "", "Hello BlockQuote")
    expect = ('blockquote', OrderedDict(), 'p', OrderedDict(),
              'Hello BlockQuote')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect

    b = Block(t, "bq", "", None, "http://google.com", "Hello BlockQuote")
    expect = ('blockquote', OrderedDict([('cite',
              '{0.uid}{0.refIndex}:url'.format(t))]), 'p', OrderedDict(),
              'Hello BlockQuote')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect

    b = Block(t, "bc", "", None, "", 'printf "Hello, World";')
    # the content of text will be turned shelved, so we'll asert only the
    # deterministic portions of the expected values, below
    expect = ('pre', OrderedDict(), 'code', OrderedDict())
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts)
    assert result == expect

    b = Block(t, "h1", "", None, "", "foobar")
    expect = ('h1', OrderedDict(), '', OrderedDict(), 'foobar')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect


def test_block_tags_false():
    t = textile.Textile(block_tags=False)
    assert t.block_tags is False

    result = t.parse('test')
    expect = 'test'
    assert result == expect


def test_blockcode_extended():
    input = 'bc.. text\nmoretext\n\nevenmoretext\n\nmoremoretext\n\np. test'
    expect = '<pre><code>text\nmoretext\n\nevenmoretext\n\nmoremoretext</code></pre>\n\n\t<p>test</p>'
    t = textile.Textile()
    result = t.parse(input)
    assert result == expect


def test_blockcode_in_README():
    with open('README.textile') as f:
        readme = ''.join(f.readlines())
    result = textile.textile(readme)
    with open('tests/fixtures/README.txt') as f:
        expect = ''.join(f.readlines())
    assert result == expect


def test_blockcode_comment():
    input = '###.. block comment\nanother line\n\np. New line'
    expect = '\t<p>New line</p>'
    t = textile.Textile()
    result = t.parse(input)
    assert result == expect


def test_extended_pre_block_with_many_newlines():
    """Extra newlines in an extended pre block should not get cut down to only
    two."""
    text = '''pre.. word

another

word


yet anothe word'''
    expect = '''<pre>word

another

word


yet anothe word</pre>'''
    result = textile.textile(text)
    assert result == expect

    text = 'p. text text\n\n\nh1. Hello\n'
    expect = '\t<p>text text</p>\n\n\n\t<h1>Hello</h1>'
    result = textile.textile(text)
    assert result == expect
