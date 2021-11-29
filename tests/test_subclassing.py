import textile


def test_change_glyphs():
    class TextilePL(textile.Textile):
        glyph_definitions = dict(textile.Textile.glyph_definitions,
                                 quote_double_open='&#8222;')

    test = 'Test "quotes".'
    expect = '\t<p>Test &#8222;quotes&#8221;.</p>'
    result = TextilePL().parse(test)
    assert expect == result

    # Base Textile is unchanged.
    expect = '\t<p>Test &#8220;quotes&#8221;.</p>'
    result = textile.textile(test)
    assert expect == result
