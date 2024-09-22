from textile import Textile


def test_lists():
    t = Textile()
    result = t.textileLists("* one\n* two\n* three")
    expect = '\t<ul>\n\t\t<li>one</li>\n\t\t<li>two</li>\n\t\t<li>three</li>\n\t</ul>'
    assert result == expect
