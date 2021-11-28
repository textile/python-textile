import textile

def test_imagesize():
    imgurl = 'http://www.google.com/intl/en_ALL/images/srpr/logo1w.png'
    result = textile.tools.imagesize.getimagesize(imgurl)
    try:
        import PIL # noqa: F401

        expect = (275, 95)
        assert result == expect
    except ImportError:
        expect = ''
        assert result == expect
