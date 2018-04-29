from textile.utils import generate_tag

class List(object):
    def __init__(self, listtype, attributes={}, indent_level=0):
        super(List, self).__init__()
        self.type = listtype
        self.attributes = attributes
        self.indent_level = indent_level
        self.items = []

    def add_item(self, tag, content, attributes={}):
        item = ListItem(tag, content, attributes)
        if type(content) is List:
            # if we are nesting lists, pop off the content of the most-recently
            # processed list, strip off the html tags for it, and tack the
            # current item content onto the end of that.
            prev = self.items.pop()
            prev_content = prev.split('>')[1].rsplit('<')[0]
            item.content = '{0}\n{1}'.format(prev_content, item.content.process())
        self.items.append(item.process())

    def process(self):
        indent = '\t' * self.indent_level
        content = '\n{0}{1}\n{0}'.format(indent, '\n{0}'.format(indent).join(self.items))
        tag = generate_tag(self.type, content, self.attributes)
        return '{0}{1}'.format(indent, tag)


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
        return '\t{0}'.format(tag)
