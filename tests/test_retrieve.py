from textile import Textile


def test_retrieve():
    t = Textile()
    id = t.shelve("foobar")
    assert t.retrieve(id) == 'foobar'
