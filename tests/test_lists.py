from textile import Textile
from textile.objects.list import List

def test_lists():
    t = Textile()
    result = t.textileLists("* one\n* two\n* three")
    expect = '\t<ul>\n\t\t<li>one</li>\n\t\t<li>two</li>\n\t\t<li>three</li>\n\t</ul>'
    assert result == expect

def test_nested_list():
    l = List('ol')
    l.add_item('li', 'test')
    s = List('ol')
    s.add_item('li', 'another one')
    l.add_item('li', s, sublist=True)
    result = l.process()
    expect = '\t<ol>\n\t\t<li>test\n\t\t<ol>\n\t\t<li>another one</li>\n\t</ol></li>\n\t</ol>'
    assert result == expect
