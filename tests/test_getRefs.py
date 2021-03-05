from textile import Textile

def test_getRefs():
    t = Textile()
    result = t.getRefs("some text [Google]http://www.google.com")
    expect = 'some text '
    assert result == expect

    result = t.urlrefs
    expect = {'Google': 'http://www.google.com'}
    assert result == expect

    t2 = Textile()

    result = t2.getRefs("my ftp [ftp]ftp://example.com")
    expect = 'my ftp '
    assert result == expect

    result = t2.urlrefs
    expect = {'ftp': 'ftp://example.com'}
    assert result == expect
