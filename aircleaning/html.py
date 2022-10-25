###############################################################################
''''''
###############################################################################


import abc as _abc
import os as _os
import itertools as _itertools
from collections import abc as _collabc


class HTML:

    standard_indent = '  '

    __slots__ = ()

    @_abc.abstractmethod
    def yield_lines(self, indent, /):
        raise NotImplementedError

    def yield_scripts(self, /):
        yield from ()

    @property
    def scripts(self, /):
        out = []
        for script in self.yield_scripts():
            if script not in out:
                out.append(script)
        return tuple(out)

    def yield_styles(self, /):
        yield from ()

    def yield_boilerplate(self, /):
        yield 0, f'''<!DOCTYPE html>'''
        yield 0, "<script>"+'\n'.join(self.scripts)+"\n"+"</script>"
        yield 0, "<style>"+'\n'.join(self.styles)+"\n"+"</style>"

    @property
    def styles(self, /):
        out = []
        for style in self.yield_styles():
            if style not in out:
                out.append(style)
        return tuple(out)

    def _repr_html_(self, /):
        standard = self.standard_indent
        out = []
        for indent, text in _itertools.chain(
                self.yield_boilerplate(),
                self.yield_lines(),
                ):
            out.append(indent*standard)
            out.append(text)
            out.append('\n')
        return ''.join(out)

    def save_html(self, /, name, path='.'):
        with open(_os.path.join(path, name) + '.html', mode='w') as file:
            file.write(self._repr_html_())


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
        super().__init__()
        if identity is None:
            identity = f"id_{id(self)}"
        if name is None:
            name = identity
        for param in ('title', 'identity', 'name', 'href'):
            val = eval(param)
            setattr(self, param, (None if val is None else str(val)))
        self.classes = tuple(map(str, classes))
        self.attributes = kwargs

    def yield_attributes(self, /):
        for param in ('title', 'name', 'href'):
            val = getattr(self, param)
            if val is not None:
                yield param, f'"{val}"'
        yield 'id', self.identity
        classes = self.classes
        if classes:
            yield 'class', ' '.join(f'"{kls}"' for kls in self.classes)
        for key, val in self.attributes.items():
            if val is None:
                continue
            if isinstance(val, bool):
                if val:
                    yield key, NotImplemented
            elif isinstance(val, str):
                yield key, f'"{val}"'
            elif isinstance(val, _collabc.Iterable):
                yield key, ' '.join(f'"{subval}"' for subval in val)
            else:
                yield key, str(val)

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


class HLine(Void):

    element_type_name = 'hr'

    __slots__ = ()


class Link(Void):

    element_type_name = 'link'

    __slots__ = ('rel', 'href')

    def __init__(self, /, rel: str, href: str, **kwargs):
        self.rel, self.href = str(rel), str(href)

    def yield_attributes(self, /):
        super().yield_attributes()
        yield 'rel', f'"{self.rel}"'
        yield 'href', f'"{self.rel}"'


class Normal(Element):

    __slots__ = ('contents',)

    def __init__(self, /, *contents, **kwargs):
        super().__init__(**kwargs)
        self.contents = ()
        self.add_content(contents)

    def yield_scripts(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_scripts()

    def yield_styles(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_styles()  

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


class Page(Normal):

    element_type_name = 'html'

    __slots__ = ('contents',)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'lang', '"en"'

    def yield_lines(self, indent=0, /):
        yield indent, f"<head>"
        yield indent+1, f'''<meta charset="UTF-8">'''
        yield indent+1, f'''<title>{self.title}</title>'''
        yield indent, f'''</head>'''
        yield from super().yield_lines(indent)

    def _yield_lines_(self, /):
        yield 0, f'''<body>'''
        yield from super()._yield_lines_()
        yield 0, f'''</body>'''


class Div(Normal):

    element_type_name = 'div'

    __slots__ = ()


class Paragraph(Normal):

    element_type_name = 'p'

    __slots__ = ()


class Textual(Normal):

    __slots__ = ()

    def __init__(self, content, /, **kwargs):
        super().__init__(str(content))


class Script(Textual):

    element_type_name = 'script'

    __slots__ = ()


class Style(Textual):

    element_type_name = 'style'

    __slots__ = ()


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

    __slots__ = ('input_type', 'value', 'oninput')

    def __init__(self, /,
            input_type: str,
            value,
            oninput="form_update(this.form)",
            **kwargs
            ):
        self.input_type = str(input_type)
        self.value = str(value)
        self.oninput = str(oninput)
        super().__init__(**kwargs)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'type', f'"{self.input_type}"'
        yield 'value', f'"{self.value}"'
        yield 'oninput', f'"{self.oninput}"'

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
            **kwargs
            ):
        super().__init__()
        if isinstance(input_type, str):
            inpel = self.input_element = Input(input_type, **kwargs)
        else:
            inpel = input_type(*args, **kwargs)
        self.label_element = Label(
            inpel.identity,
            label_content,
            identity=f"{inpel.identity}_label",
            )

    def yield_lines(self, indent=0, /):
        yield from self.input_element.yield_lines(indent)
        yield from self.label_element.yield_lines(indent)


class Output(Normal):

    element_type_name = 'output'

    __slots__ = ('idsfor',)

    def __init__(self, /, idsfor: tuple, value, **kwargs):
        super().__init__(value, **kwargs)
        if isinstance(idsfor, str):
            self.idsfor = (idsfor,)
        else:
            self.idsfor = tuple(map(str, idsfor))

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        idsfor = ' '.join(self.idsfor)
        yield 'for', f'"{idsfor}"'


class CapturedInput(Div):

    __slots__ = ()

    def __init__(
            self, /, input_type, *args,
            oninput=("this.nextElementSibling.value=this.value;"
                     "form_update(this.form)"),
            input_kwargs=None, output_kwargs=None, **kwargs
            ):
        input_kwargs = {} if input_kwargs is None else input_kwargs
        if isinstance(input_type, str):
            inpel = Input(input_type, *args, oninput=oninput, **input_kwargs)
        else:
            inpel = input_type(*args, oninput=oninput, **input_kwargs)
        output = Output((inpel.identity,), '-')
        super().__init__(inpel, output, **kwargs)


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


class ValueSlider(Div):

    __slots__ = ()

    def __init__(self, /, **kwargs):
        inpel = Input('range', **kwargs)
        super().__init__(inpel)


class Button(Normal):

    element_type_name = 'button'

    __slots__ = ()


class Pane(Div):

    __slots__ = ('tab',)

    def __init__(self, tab, pane_class, /, *args, classes=(), **kwargs):
        super().__init__(*args, classes=(*classes, pane_class,), **kwargs)
        self.tab = tab


class TabbedPanes(Div):

    PANE_SELECTOR_CLASS = 'pane_selector'
    PANE_SPACE_CLASS = 'pane_space'

    __slots__ = ('panes', 'pane_class', 'button_class')

    def __init__(self, /, *args, **kwargs):
        super().__init__(**kwargs)
        pane_class = self.pane_class = f"{self.identity}_pane"
        button_class = self.button_class = f"{pane_class}_button"
        panes = Div(*(
            Pane(content.identity, pane_class, content) for content in args
            ), classes=(self.PANE_SPACE_CLASS,))
        pane_selector = Div(*(
            Button(
                pane.tab, classes=(button_class,),
                onclick=f'''openPane(event, '{pane_class}', '{pane.identity}')''',
                )
            for pane in panes.contents
            ), classes=(self.PANE_SELECTOR_CLASS,))
        self.add_content((pane_selector, panes))

    def yield_scripts(self, /):
        yield from super().yield_scripts()
        yield '\n' + '\n'.join((
            '''function openPane(evt, paneClass, paneName) {''',
            '''  // Declare all variables''',
            '''  var i, tabcontent, tablinks;''',
            '''  // Get all elements with class=<paneClass> and hide them''',
            '''  tabcontent = document.getElementsByClassName(paneClass);''',
            '''  for (i = 0; i < tabcontent.length; i++) {''',
            '''    tabcontent[i].style.display = "none";''',
            '''  }''',
            '''  // Get all elements with class="<paneClass>_button"''',
            '''  // and remove the class "active"''',
            '''  tablinks = document.getElementsByClassName(paneClass+"_button");''',
            '''  for (i = 0; i < tablinks.length; i++) {''',
            '''    tablinks[i].className = tablinks[i].className.replace(" active", "");''',
            '''  }''',
            '''  // Show the current tab''',
            '''  // and add an "active" class to the button that opened the tab''',
            '''  document.getElementById(paneName).style.display = "block";''',
            '''  evt.currentTarget.className += " active";''',
            '''  }''',
            ))

    def yield_styles(self, /):
        yield from super().yield_styles()
        yield '\n' + '\n'.join((
            "/* Style the tab */",
            f".{self.PANE_SELECTOR_CLASS} {{",
            "  overflow: hidden;",
            "  border: 1px solid #ccc;",
            "  background-color: #f1f1f1;",
            "}",
            ))
        yield '\n' + '\n'.join((
            "/* Style the buttons that are used to open the tab content */",
            f".{self.PANE_SELECTOR_CLASS} button {{",
            "  background-color: inherit;",
            "  float: left;",
            "  border: none;",
            "  outline: none;",
            "  cursor: pointer;",
            "  padding: 14p 16px;",
            "  transition: 0.3s;",
            "}"
            ))
        yield '\n' + '\n'.join((
            "/* Change background color of buttons on hover */",
            f".{self.PANE_SELECTOR_CLASS} button:hover {{",
            "  background-color: #ddd;",
            "}",
            ))
        yield '\n' + '\n'.join((
            "/* Create an active/current tablink class */",
            f".{self.PANE_SELECTOR_CLASS} button.active {{",
            "  background-color: #ccc;",
            "}",
            ))
        yield '\n' + '\n'.join((
            "/* Style the tab content */",
            f".{self.pane_class} {{",
            "  display: none;",
            "  padding: 6px 12px;",
            "  border: 1px solid #ccc;",
            "  border-top: none;",
            "  animation: fadeEffect 1s;",
            "}"
            ))
        yield '\n' + '\n'.join((
            '''@keyframes fadeEffect {''',
            '''  from {opacity: 0;}''',
            '''  to {opacity: 1;}''',
            '''}''',
            ))



###############################################################################
###############################################################################
