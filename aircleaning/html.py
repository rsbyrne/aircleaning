###############################################################################
''''''
###############################################################################


import abc as _abc


class HTML:

    standard_indent = '  '

    __slots__ = ()

    @_abc.abstractmethod
    def yield_lines(self, indent, /):
        raise NotImplementedError

    def _repr_html_(self, /):
        standard = self.standard_indent
        out = []
        for indent, text in self.yield_lines():
            out.append(indent*standard)
            out.append(text)
            out.append('\n')
        return ''.join(out)


class Element(HTML):

    __slots__ = (
        'title', 'identity', 'name', 'href', 'classes',
        'attributes',
        )

    element_type_name = ''

    def __init__(self, /, *,
            title: str = None,
            identity: str = None,
            name: str = None,
            href: str = None,
            classes: tuple = (),
            **kwargs,
            ):
        if identity is None:
            identity = str(id(self))
        if name is None:
            name = identity
        for param in ('title', 'identity', 'name', 'href'):
            val = eval(param)
            setattr(self, param, (None if val is None else str(val)))
        self.classes = tuple(map(str, classes))
        self.attributes = kwargs

    def yield_attributes(self, /):
        for param in ('title', 'identity', 'name', 'href'):
            val = getattr(self, param)
            if val is not None:
                yield param, f'"{val}"'
        classes = self.classes
        if classes:
            yield 'class', ' '.join(f'"{kls}"' for kls in self.classes)
        for key, val in self.attributes.items():
            if val is None:
                continue
            if isinstance(val, bool):
                if val:
                    yield key, NotImplemented
            else:
                yield key, f'"{val}"'

    def yield_lines(self, indent=0, /):
        yield indent, f'<{self.element_type_name}'
        for attrname, attr in self.yield_attributes():
            if attr is NotImplemented:
                yield indent+1, attrname
            else:
                yield indent+1, f'{attrname}={attr}'
        yield indent, f'>'


class Void(Element):

    __slots__ = ()


class Normal(Element):

    __slots__ = ('contents',)

    def __init__(self, /, *contents, **kwargs):
        super().__init__(**kwargs)
        self.contents = ()
        self.add_content(contents)

    def add_content(self, content, /):
        if content is None:
            return
        if isinstance(content, (str, HTML)):
            contents = (content,)
        else:
            contents = tuple(content)
        self.contents = (*self.contents, *content)

    def _yield_lines_(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_lines(1)
            else:
                yield 1, content

    def yield_lines(self, indent=0, /):
        yield from super().yield_lines(indent)
        for subind, line in self._yield_lines_():
            yield subind+1, line
        yield indent, f"</{self.element_type_name}>"


class Div(Normal):

    element_type_name = 'div'

    __slots__ = ()


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

    __slots__ = ()


class Fieldset(Normal):

    element_type_name = 'fieldset'

    __slots__ = ('legend', 'formfields')

    def __init__(self, /, legend, *args, **kwargs):
        if not isinstance(legend, Legend):
            legend = Legend(legend)
        super().__init__(legend, *args, **kwargs)


class Legend(Normal):

    element_type_name = 'legend'

    __slots__ = ()


class Input(Void):

    element_type_name = 'input'

    __slots__ = ('input_type',)

    def __init__(self, /,
            input_type: str,
            **kwargs
            ):
        self.input_type = str(input_type)
        super().__init__(**kwargs)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'type', f'"{self.input_type}"'

    # def yield_lines(self, indent=0, /):
    #     yield from super().yield_lines()


class Label(Normal):

    element_type_name = 'label'

    __slots__ = ('isfor',)

    def __init__(self, /, isfor: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isfor = str(isfor)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'for', f'"{self.isfor}"'


class LabelledInput(HTML):

    __slots__ = ('input_element', 'label_element')

    def __init__(
            self, /,
            label_content: (str, tuple),
            input_type: str,
            *args, **kwargs
            ):
        super().__init__()
        inpel = self.input_element = Input(input_type, *args, **kwargs)
        self.label_element = Label(
            inpel.identity,
            label_content,
            identity=f"{inpel.identity}_label",
            )

    def yield_lines(self, indent=0, /):
        yield from self.input_element.yield_lines(indent)
        yield from self.label_element.yield_lines(indent)


class RadioSet(Fieldset):

    __slots__ = ()

    def __init__(self, /, legend, values, default=None, **kwargs):
        super().__init__(legend, **kwargs)
        values = tuple(map(str, values))
        self.add_content(tuple(
            LabelledInput(
                value, 'radio', name=self.name, value=value, required=True,
                checked=(value == default),
                )
            for value in values
            ))


###############################################################################
###############################################################################
