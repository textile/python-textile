from textile.utils import generate_tag

class List(object):
    def __init__(self, listtype, attributes={}):
        super(List, self).__init__()
        self.type = listtype
        self.attributes = attributes
        self.items = []

    def add_item(self, tag, content, attributes={}):
        item = ListItem(tag, content, attributes)
        self.items.append(item.process())

    def process(self):
        content = '\n\t\t{0}\n\t'.format('\n\t\t'.join(self.items))
        tag = generate_tag(self.type, content, self.attributes)
        return '\t{0}'.format(tag)


class ListItem(object):
    def __init__(self, tag, content, attributes={}):
        super(ListItem, self).__init__()
        self.tag = tag
        self.content = content
        self.attributes = attributes

    def process(self):
        if isinstance(self.content, List):
            return self.content.process()
        tag = generate_tag(self.tag, self.content, self.attributes)
        return '{0}'.format(tag)
