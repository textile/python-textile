from urllib.request import urlopen


def getimagesize(url):
    """
    Attempts to determine an image's width and height, and returns a tuple,
    (width, height), in pixels or an empty string in case of failure.
    Requires that PIL is installed.

    """

    try:
        from PIL import ImageFile
    except ImportError:
        return ''

    try:
        p = ImageFile.Parser()
        f = urlopen(url)
        while True:
            s = f.read(1024)
            if not s:
                break
            p.feed(s)
            if p.image:
                return p.image.size
    except (IOError, ValueError):
        return ''
