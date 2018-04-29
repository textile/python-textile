from textile import Textile
from textile.objects.list import List


def test_lists():
    t = Textile()
    result = t.textileLists("* one\n* two\n* three")
    expect = '\t<ul>\n\t\t<li>one</li>\n\t\t<li>two</li>\n\t\t<li>three</li>\n\t</ul>'
    assert result == expect

def test_nested_list():
    l = List('ol', indent_level=1)
    l.add_item('li', 'test')
    s = List('ol', indent_level=2)
    s.add_item('li', 'another one')
    l.add_item('li', s)
    result = l.process()
    expect = '\t<ol>\n\t\t<li>test\n\t\t<ol>\n\t\t\t<li>another one</li>\n\t\t</ol></li>\n\t</ol>'
    assert result == expect

    l = List('ol', indent_level=1)
    l.add_item('li', 'test')
    s1 = List('ol', indent_level=2)
    s1.add_item('li', 'another one')
    s2 = List('ul', indent_level=3)
    s2.add_item('li', 'point one')
    s2.add_item('li', 'point two')
    s1.add_item('li', s2)
    s1.add_item('li', 'moar item')
    l.add_item('li', s1)
    result = l.process()
    expect = '\t<ol>\n\t\t<li>test\n\t\t<ol>\n\t\t\t<li>another one\n\t\t\t<ul>\n\t\t\t\t<li>point one</li>\n\t\t\t\t<li>point two</li>\n\t\t\t</ul></li>\n\t\t\t<li>moar item</li>\n\t\t</ol></li>\n\t</ol>'
    assert result == expect
