###############################################################################
''''''
###############################################################################


import abc as _abc


class Element:

    element_type_name = ''
    standard_indent = '  '

    def yield_attributes(self, /):
        yield from ()

    @_abc.abstractmethod
    def yield_lines(self, indent, /):
        yield indent, f'<{self.element_type_name}'
        for attrname, attr in self.yield_attributes():
            yield indent+1, f'''{attrname}={attr}'''
        yield indent, f'>'

    def _repr_html_(self, /):
        standard = self.standard_indent
        out = []
        for indent, text in self.yield_lines():
            out.append(indent*standard)
            out.append(text)
            out.append('\n')
        return ''.join(out)


class Void(Element):

    ...


class Normal(Element):

    def _yield_lines_(self, /):
        yield from ()

    def yield_lines(self, indent=0, /):
        yield from super().yield_lines(indent)
        for subind, line in self._yield_lines_():
            yield subind+1, line
        yield indent, f"</{self.element_type_name}>"


class Page(Normal):

    element_type_name = 'html'

    __slots__ = ('title', 'contents')

    def __init__(self, /, title, contents=()):
        self.title = title
        self.contents = tuple(contents)

    def yield_attributes(self, /):
        yield 'lang', '"en"'

    def yield_lines(self, indent=0, /):
        yield indent, f'''<!DOCTYPE html>'''
        yield indent, f"<head>"
        yield indent+1, f'''<meta charset="UTF-8">'''
        yield indent+1, f'''<title>{self.title}</title>'''
        yield indent, f'''</head>'''
        yield from super().yield_lines(indent)

    def _yield_lines_(self, /):
        yield 0, f'''<body>'''
        for content in self.contents:
            yield from content.yield_lines(1)
        yield 0, f'''</body>'''


###############################################################################
###############################################################################
