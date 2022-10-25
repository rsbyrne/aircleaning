###############################################################################
''''''
###############################################################################


import abc as _abc


class HTML:

    __slots__ = ()

    @_abc.abstractmethod
    def yield_lines(self, indent, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def _repr_html_(self, /):
        raise NotImplementedError


class Element:

    __slots__ = ('title', 'identity', 'name', 'href', 'classes')

    element_type_name = ''
    standard_indent = '  '

    def __init__(self, /, *,
            title: str = None,
            identity: str = None,
            name: str = None,
            href: str = None,
            classes: tuple = ()
            ):
        if identity is None:
            identity = str(id(self))
        for param in ('title', 'identity', 'name', 'href'):
            val = eval(param)
            setattr(self, param, (None if val is None else str(val)))
        self.classes = tuple(map(str, classes))

    def yield_attributes(self, /):
        for param in ('title', 'identity', 'name', 'href'):
            val = getattr(self, param)
            if val is not None:
                yield param, f'"{val}"'
        yield 'class', ' '.join(f'"{kls}"' for kls in self.classes)

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

    __slots__ = ()


class Normal(Element):

    __slots__ = ('contents',)

    def __init__(self, /, *args, contents=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.contents = tuple(contents)

    def _yield_lines_(self, /):
        for content in self.contents:
            if isinstance(content, Element):
                yield from content.yield_lines(1)
            else:
                yield 1, content

    def yield_lines(self, indent=0, /):
        yield from super().yield_lines(indent)
        for subind, line in self._yield_lines_():
            yield subind+1, line
        yield indent, f"</{self.element_type_name}>"


class Page(Normal):

    element_type_name = 'html'

    __slots__ = ('title', 'contents')

    def yield_attributes(self, /):
        yield from super().yield_attributes()
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
        yield from super()._yield_lines_()
        yield 0, f'''</body>'''


class Form(Normal):

    element_type_name = 'form'


class Input(Void):

    __slots__ = ('input_type',)

    def __init__(self, /,
            input_type: str,
            *args,
            **kwargs
            ):
        self.input_type = str(input_type)
        super().__init__(*args, **kwargs)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'type', f'"{self.input_type}"'

    # def yield_lines(self, indent=0, /):
    #     yield from super().yield_lines()


class Label(Normal):

    element_type_name = 'label'

    def __init__(self, /, isfor: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isfor = str(isfor)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'for', f'"{self.isfor}"'


###############################################################################
###############################################################################
