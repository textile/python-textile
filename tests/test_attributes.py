from textile.utils import parse_attributes


def test_parse_attributes():
    assert parse_attributes('\\1', element='td') == {'colspan': '1'}
    assert parse_attributes('/1', element='td') == {'rowspan': '1'}
    assert parse_attributes('^', element='td') == {'style': 'vertical-align:top;'}
    assert parse_attributes('{color: blue}') == {'style': 'color: blue;'}
    assert parse_attributes('[en]') == {'lang': 'en'}
    assert parse_attributes('(cssclass)') == {'class': 'cssclass'}
    assert parse_attributes('(') == {'style': 'padding-left:1em;'}
    assert parse_attributes(')') == {'style': 'padding-right:1em;'}
    assert parse_attributes('<') == {'style': 'text-align:left;'}
    assert parse_attributes('(c#i)') == {'class': 'c', 'id': 'i'}
    assert parse_attributes('\\2 100', element='col') == {'span': '2', 'width': '100'}
