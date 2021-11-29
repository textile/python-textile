from textile import Textile


def test_span():
    t = Textile()
    result = t.span("hello %(bob)span *strong* and **bold**% goodbye")
    expect = ('hello <span class="bob">span <strong>strong</strong> and '
              '<b>bold</b></span> goodbye')
    assert result == expect

    result = t.span('%:http://domain.tld test%')
    expect = '<span cite="http://domain.tld">test</span>'
    assert result == expect

    t = Textile()
    # cover the partial branch where we exceed the max_span_depth.
    t.max_span_depth = 2
    result = t.span('_-*test*-_')
    expect = '<em><del>*test*</del></em>'
    assert result == expect
