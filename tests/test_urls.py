# -*- coding: utf-8 -*-
from textile import Textile


def test_urls():
    t = Textile()
    assert t.relURL("http://www.google.com/") == 'http://www.google.com/'

    result = t.links('fooobar "Google":http://google.com/foobar/ and hello world "flickr":http://flickr.com/photos/jsamsa/ ')
    expect = 'fooobar {0}2:shelve and hello world {0}4:shelve '.format(t.uid)
    assert result == expect

    result = t.links('""Open the door, HAL!"":https://xkcd.com/375/')
    expect = '{0}6:shelve'.format(t.uid)
    assert result == expect

    result = t.links('"$":http://domain.tld/test_[brackets]')
    expect = '{0}8:shelve'.format(t.uid)
    assert result == expect

    result = t.links('<em>"$":http://domain.tld/test_</em>')
    expect = '<em>{0}10:shelve</em>'.format(t.uid)
    assert result == expect

    expect = '"":test'
    result = t.links(expect)
    assert result == expect

    expect = '"$":htt://domain.tld'
    result = t.links(expect)
    assert result == expect

    result = t.shelveURL('')
    expect = ''
    assert result == expect

    result = t.retrieveURLs('{0}2:url'.format(t.uid))
    expect = ''
    assert result == expect

    result = t.encode_url('http://domain.tld/übermensch')
    expect = 'http://domain.tld/%C3%BCbermensch'
    assert result == expect

    result = t.parse('A link that starts with an h is "handled":/test/ incorrectly.')
    expect = '\t<p>A link that starts with an h is <a href="/test/">handled</a> incorrectly.</p>'
    assert result == expect

    result = t.parse('A link that starts with a space" raises":/test/ an exception.')
    expect = '\t<p><a href="/test/">A link that starts with a space&#8221; raises</a> an exception.</p>'
    assert result == expect

    result = t.parse('A link that "contains a\nnewline":/test/ raises an exception.')
    expect = '\t<p>A link that <a href="/test/">contains a\nnewline</a> raises an exception.</p>'
    assert result == expect


def test_rel_attribute():
    t = Textile(rel='nofollow')
    result = t.parse('"$":http://domain.tld')
    expect = '\t<p><a href="http://domain.tld" rel="nofollow">domain.tld</a></p>'
    assert result == expect


def test_quotes_in_link_text():
    """quotes in link text are tricky."""
    test = '""this is a quote in link text"":url'
    t = Textile()
    result = t.parse(test)
    expect = '\t<p><a href="url">&#8220;this is a quote in link text&#8221;</a></p>'
    assert result == expect


def test_ipv6_literal_link_keeps_single_closing_bracket():
    t = Textile()
    assert t.parse('"host":http://[2001:db8::1]/') == (
        '\t<p><a href="http://[2001:db8::1]">host</a>/</p>')
    assert t.parse('"loopback":http://[::1]/') == (
        '\t<p><a href="http://[::1]">loopback</a>/</p>')
    assert t.parse('"port":http://[::1]:8080/') == (
        '\t<p><a href="http://[::1]">port</a>:8080/</p>')
    assert t.parse('"creds":http://user:pass@[::1]:8080/') == (
        '\t<p><a href="http://user:pass@[::1]">creds</a>:8080/</p>')


def test_unmatched_bracket_before_query_still_pops():
    t = Textile()
    # Master pops trailing after an unmatched ]; IPv6 reattach must not change that.
    assert t.parse('"t":http://example.com/x]?q=1') == (
        '\t<p><a href="http://example.com/x">t</a>?q=1</p>')
    assert t.parse('"test":http://example.com/x]=foo') == (
        '\t<p><a href="http://example.com/x%5D%3Dfoo">test</a></p>')


def test_link_url_ending_in_angle_bracket():
    """A link whose URL ends in '>' with no closing tag used to raise a raw
    AttributeError; the '>' should be dropped completely from the URL and
    the output to align with reference php-textile."""
    t = Textile()
    assert t.parse('"a":b>') == '\t<p><a href="b">a</a></p>'
    assert t.parse('"x":http://x.com/>') == (
        '\t<p><a href="http://x.com/">x</a></p>')
    # A genuine trailing closing tag is still absorbed as before.
    assert t.parse('"y":http://x.com/</a') == (
        '\t<p><a href="http://x.com/%3C/a">y</a></p>')
    assert t.parse('"y":http://x.com/</a>') == (
        '\t<p><a href="http://x.com/">y</a></a></p>')
