from textile import Textile


def test_footnoteRef():
    t = Textile()
    result = t.footnoteRef('foo[1]')
    expect = 'foo<sup class="footnote" id="fnrev{0}1"><a href="#fn{0}1">1</a></sup>'.format(t.linkPrefix)
    assert expect == result
