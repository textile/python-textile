from textile import Textile


def test_glyphs():
    t = Textile()

    result = t.glyphs("apostrophe's")
    expect = 'apostrophe&#8217;s'
    assert result == expect

    result = t.glyphs("back in '88")
    expect = 'back in &#8217;88'
    assert result == expect

    result = t.glyphs('foo ...')
    expect = 'foo &#8230;'
    assert result == expect

    result = t.glyphs('--')
    expect = '&#8212;'
    assert result == expect

    result = t.glyphs('FooBar[tm]')
    expect = 'FooBar&#8482;'
    assert result == expect

    result = t.glyphs("<p><cite>Cat's Cradle</cite> by Vonnegut</p>")
    expect = '<p><cite>Cat&#8217;s Cradle</cite> by Vonnegut</p>'
    assert result == expect
