###############################################################################
''''''
###############################################################################


import abc as _abc


class Element:

    element_type_name = ''

    def _yield_lines_(self, indent, /):
        yield from ()

    @_abc.abstractmethod
    def yield_lines(self, indent, /):
        raise NotImplementedError

    def _repr_html_(self, /):
        return '\n'.join(self.yield_lines()) + '\n'


class Void(Element):

    def _repr_html_(self, /):


class Normal(Element):



    @property
    def open_tag(self, /):
        return f"<{self.element_type_name}>"

    @property
    def close_tag(self, /):
        return f"</{self.element_type_name}>"

    def yield_lines(self, indent=0, /):
        ind = indent * '  '
        yield ind + self.open_tag
        for line in self._yield_lines_(indent):
            yield ind + line
        yield ind + self.close_tag


class Page(Element):

    __slots__ = ('title', 'contents')

    def __init__(self, /, title, contents=()):
        self.title = title
        self.contents = tuple(contents)

    def _yield_lines_(self, indent, /):
        yield f'''<!DOCTYPE html>'''
        yield f'''<html lang="en">'''
        yield f'''<head>'''
        yield f'''  <meta charset="UTF-8">'''
        yield f'''  <title>{self.title}</title>'''
        yield f'''</head>'''
        yield f'''<body>'''
        for content in self.contents:
            yield from content.yield_lines(1)
        yield f'''</body>'''
        yield f'''</html>'''


###############################################################################
###############################################################################
