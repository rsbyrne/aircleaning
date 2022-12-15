###############################################################################
''''''
###############################################################################


import os as _os
import itertools as _itertools
from collections import abc as _collabc


class HTML:

    STANDARD_INDENT = '  '

    __slots__ = ()

    def yield_lines(self, indent=0, /):
        yield from ()

    def yield_inits(self, /):
        yield from ()

    @property
    def inits(self, /):
        out = []
        for init in self.yield_inits():
            if not isinstance(init, str):
                init = tuple(init)
            if init not in out:
                out.append(init)
        return tuple(out)

    def yield_scripts(self, /):
        yield from ()

    @property
    def scripts(self, /):
        out = []
        for script in self.yield_scripts():
            if not isinstance(script, str):
                script = tuple(script)
            if script not in out:
                out.append(script)
        return tuple(out)

    def yield_styles(self, /):
        yield from ()

    def yield_boilerplate(self, /):
        yield 0, f'''<!DOCTYPE html>'''
        yield 0, "<script>"
        for content in self.scripts:
            if isinstance(content, str):
                yield 1, content
            else:
                for line in content:
                    yield 1, line
        yield 1, "</script>"
        yield 0, "<style>"
        for content in self.styles:
            if isinstance(content, str):
                yield 1, content
            else:
                for line in content:
                    yield 1, line
        yield 1, "</style>"

    def yield_initialiser(self, /):
        yield 0, "<script>"
        for content in self.inits:
            if isinstance(content, str):
                yield 1, content
            else:
                for line in content:
                    yield 1, line
        yield 1, "</script>"

    @property
    def styles(self, /):
        out = []
        for style in self.yield_styles():
            if not isinstance(style, str):
                style = tuple(style)
            if style not in out:
                out.append(style)
        return tuple(out)

    def _repr_html_(self, /):
        standard = self.STANDARD_INDENT
        out = []
        for indent, text in _itertools.chain(
                self.yield_boilerplate(),
                self.yield_lines(),
                self.yield_initialiser(),
                ):
            if text:
                out.append(indent*standard)
                out.append(text)
            out.append('\n')
        return ''.join(out)

    def save_html(self, /, name, path='.'):
        with open(_os.path.join(path, name) + '.html', mode='w') as file:
            file.write(self._repr_html_())
        return


class Element(HTML):

    __slots__ = (
        'title', 'identity', 'name', 'href', 'classes', 'instyles',
        'attributes',
        )

    element_type_name = ''

    def __init__(self, /, *,
            title: str = None,
            identity: str = None,
            name: str = None,
            href: str = None,
            classes: tuple = (),
            instyles: tuple = (),
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
        if isinstance(classes, str):
            classes = (classes,)
        else:
            classes = tuple(classes)
        classes = (*classes, *self.yield_classes())
        self.classes = tuple(sorted(set(map(str, classes))))
        if isinstance(instyles, str):
            instyles = (instyles,)
        else:
            instyles = tuple(instyles)
        self.instyles = instyles
        self.attributes = kwargs

    def yield_classes(self, /):
        return
        yield

    def yield_attributes(self, /):
        for param in ('title', 'name', 'href'):
            val = getattr(self, param)
            if val is not None:
                yield param, f'"{val}"'
        yield 'id', f'"{self.identity}"'
        classes = self.classes
        if classes:
            yield 'class', f'''"{' '.join(self.classes)}"'''
        instyles = self.instyles
        if instyles:
            yield 'style', '"' + '; '.join(instyles) + '"'
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
        yield from super().yield_lines(indent)
        yield indent, f'<{self.element_type_name}'
        for attrname, attr in self.yield_attributes():
            if attr is NotImplemented:
                yield indent+2, attrname
            else:
                yield indent+2, f'{attrname}={attr}'
        yield indent+2, f'>'


class Custom(Element):

    def yield_prototype(self, /):
        yield from ()
        # var apeProto = Object.create(HTMLElement.prototype);
        # apeProto.hoot = function() {
        #   console.log('Apes are great!');
        # }
# document.registerElement('great-apes', {prototype: apeProto});


class Void(Element):

    __slots__ = ()


class Normal(Element):

    __slots__ = ('contents',)

    def __init__(self, /, *contents, **kwargs):
        super().__init__(**kwargs)
        self.contents = ()
        self.add_contents(*contents)

    def yield_scripts(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_scripts()

    def yield_styles(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_styles()

    def yield_inits(self, /):
        for content in self.contents:
            if isinstance(content, HTML):
                yield from content.yield_inits()

    def add_contents(self, /, *contents):
        self.contents = (*self.contents, *contents)

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
        yield indent+1, f"</{self.element_type_name}>"


class HLine(Void):

    element_type_name = 'hr'

    __slots__ = ()


class Image(Void):

    element_type_name = 'img'

    __slots__ = ('src', 'alt')

    def __init__(self, /, src, alt='', **kwargs):
        super().__init__(**kwargs)
        self.src = str(src)
        self.alt = str(alt)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'src', f'"{self.src}"'
        yield 'alt', f'"{self.alt}"'


class RemoteResource(Void):

    element_type_name = 'link'

    __slots__ = ('rel',)

    def __init__(self, /, rel: str, href: str, **kwargs):
        super().__init__(href=href, rel=rel, **kwargs)
        self.rel = str(rel)


# class RemoteScript(Void):

#     element_type_name = 'script'

#     __slots__ = ('src', 'integrity', 'crossorigin')

#     def __init__(
#             self, /,
#             src: str, integrity: str = None, crossorigin: str = None,
#             **kwargs,
#             ):
#         super().__init__(**kwargs)
#         self.src, self.integrity, self.crossorigin = \
#             map(str, (src, integrity, crossorigin))

#     def yield_attributes(self, /):
#         yield from super().yield_attributes()
#         yield 'src', f'"{self.src}"'
#         if (integrity := self.integrity) is not None:
#             yield 'integrity', f'"{self.integrity}"'
#         if (crossorigin := self.crossorigin) is not None:
#             yield 'crossorigin', f'"{self.crossorigin}"'


class Page(Normal):

    element_type_name = 'html'

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'lang', '"en"'

    def yield_lines(self, indent=0, /):
        yield indent, f"<head>"
        yield indent+1, f'''<meta charset="UTF-8">'''
        yield indent+1, f'''<title>{self.title}</title>'''
        yield indent+1, f'''</head>'''
        yield from super().yield_lines(indent)

    def _yield_lines_(self, /):
        yield 0, f'''<body class="solid">'''
        yield from super()._yield_lines_()
        yield 1, f'''</body>'''

    # def yield_classes(self, /):
    #     yield from super().yield_classes()
    #     yield 'solid'


class Span(Normal):

    element_type_name = 'span'

    __slots__ = ()


class Hyperlink(Normal):

    element_type_name = 'a'

    __slots__ = ('href',)

    def __init__(self, /, href: str, *args, **kwargs):
        super().__init__(*args, href=href, **kwargs)


class Div(Normal):

    element_type_name = 'div'

    __slots__ = ()


class Paragraph(Normal):

    element_type_name = 'p'

    __slots__ = ()


class Textual(Normal):

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*map(str, args), **kwargs)


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

    __slots__ = ('legend',)

    def __init__(self, /, legend, fields, *args, **kwargs):
        if not isinstance(legend, Legend):
            legend = Legend(legend)
        if isinstance(fields, dict):
            fields = tuple(
                LabelledInput(key, val)
                for key, val in fields.items()
                )
        elif isinstance(fields, HTML):
            fields = (fields,)
        super().__init__(legend, *fields, *args, **kwargs)


class Legend(Normal):

    element_type_name = 'legend'

    __slots__ = ()


class Input(Void):

    element_type_name = 'input'

    __slots__ = ('input_type', 'value', 'trigger')

    def __init__(self, /,
            input_type: str,
            value,
            **kwargs,
            ):
        self.input_type = str(input_type)
        self.value = str(value)
        if self.input_type == 'checkbox':
            self.trigger = (
                'onclick',
                ("if (this.value==0){this.value=1}else{this.value=0};"
                 "form_update(this.form)"),
                )
        else:
            self.trigger = ('oninput', "form_update(this.form)")
        super().__init__(**kwargs)

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'type', f'"{self.input_type}"'
        yield 'value', f'"{self.value}"'
        attrname, attr = self.trigger
        yield attrname, f'"{attr}"'

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


class LabelledInput(Div):

    __slots__ = ('input_element', 'label_element')

    def __init__(
            self, /,
            label_content: (str, tuple),
            input_element: str,
            *args,
            **kwargs
            ):
        if not isinstance(input_element, HTML):
            if isinstance(input_element, str):
                input_element = Input(input_element, *args)
            else:
                input_element = input_element(*args)
        self.input_element = input_element
        label_element = self.label_element = Label(
            input_element.identity,
            label_content,
            identity=f"{input_element.identity}_label",
            )
        super().__init__(label_element, input_element, **kwargs)


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
        output = Output((inpel.identity,), inpel.value)
        super().__init__(inpel, output, **kwargs)


class RadioSet(Fieldset):

    __slots__ = ()

    def __init__(self, /, setname, legend, values, default=None, **kwargs):
        fields = {
            value: Input(
                'radio', name=setname, value=value,
                required=True, checked=(value == default)
                )
            for value in values
            }
        super().__init__(legend, fields, **kwargs)


class ValueSlider(Div):

    __slots__ = ()

    def __init__(self, /, **kwargs):
        inpel = Input('range', **kwargs)
        super().__init__(inpel)


class Button(Normal):

    element_type_name = 'button'

    __slots__ = ()

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield "type", "button"


class Pane(Div):

    __slots__ = ('tab',)

    def __init__(self, tab, pane_class, /, *args, classes=(), **kwargs):
        super().__init__(*args, classes=(*classes, pane_class,), **kwargs)
        self.tab = tab


class TooltipOriginator(Normal):

    element_type_name = 'tooltip-originator'

    __slots__ = ()

    def __init__(self, content, /, **kwargs):
        super().__init__(content, **kwargs)

    def yield_styles(self, /):
        yield from super().yield_styles()
        yield (
            '''tooltip-originator {''',
            '''  position: relative;''',
            '''  display: inline-block;''',
            '''  border-bottom: 1px dotted blue;''',
            '''  cursor: help;''',
            '''  }''',
            )


class TooltipDestination(Normal):

    __slots__ = ()

    element_type_name = 'tooltip-destination'

    def __init__(self, content, /, **kwargs):
        super().__init__(content, **kwargs)

    def yield_classes(self, /):
        yield from super().yield_classes()
        yield 'solid'

    def yield_styles(self, /):
        yield from super().yield_styles()
        yield (
            '''tooltip-destination {''',
            # '''  width: 425px;'''
            # '''  min-height: 200px;''',
            # '''  height: auto;''',
            '''  padding: 15px;''',
            # '''  font-size: 25px;''',
            # '''  background: white;''',
            # '''  backdrop-filter: blur(5px);'''
            # '''  box-shadow: 0 30px 90px -20px rgba(0,0,0,1);''',
            '''  box-shadow: 0px 0px 10px black;''',
            '''  position: absolute;''',
            '''  z-index: 100;'''
            '''  display: none;'''
            '''  opacity: 0;''',
            '''  }''',
            )


class Tooltip(Normal):

    element_type_name = 'tooltip'

    __slots__ = ('originator', 'destination')

    def __init__(self, originator, destination, /, **kwargs):
        super().__init__(**kwargs)
        originator = self.originator = TooltipOriginator(originator)
        destination = self.destination = TooltipDestination(destination)
        self.add_contents(originator, destination)

    def yield_styles(self, /):
        yield from super().yield_styles()
        yield (
            '''@keyframes tooltip-active-anim {''',
            '''  0% {''',
            '''    opacity: 0;''',
            '''    }'''
            '''  100% {''',
            '''    opacity: 1;''',
            '''    }''',
            '''  }''',
            )
        yield (
            '''.tooltip-active {''',
            '''  display: block;''',
            '''  animation: tooltip-active-anim 0.2s linear forwards;''',
            '''  }''',
            )
        yield (
            '''@keyframes tooltip-inactive-anim {''',
            '''  0% {''',
            '''    opacity: 1;''',
            '''    }'''
            '''  100% {''',
            '''    opacity: 0;''',
            '''    }''',
            '''  }''',
            )
        yield (
            '''.tooltip-inactive {''',
            '''  display: block;''',
            '''  animation: tooltip-inactive-anim 0.2s linear forwards;''',
            '''  }''',
            )

    def yield_scripts(self, /):
        yield from super().yield_scripts()
        yield (
            '''function initialise_tooltips() {''',
            '''  const tooltips = Array.from(document.querySelectorAll("tooltip"));''',
            '''  let originator, destination;''',
            '''  let bottom;''',
            '''  tooltips.forEach((tooltip) => {''',
            '''    originator = tooltip.firstElementChild;''',
            '''    destination = tooltip.lastElementChild;''',
            '''    originator.addEventListener("mouseenter", (event) => {''',
            '''      destination.classList.remove("tooltip-inactive");''',
            '''      destination.classList.add("tooltip-active");''',
            '''      bottom = originator.offsetTop + originator.offsetHeight;''',
            '''      destination.style.left=`${originator.offsetLeft}px`;''',
            '''      destination.style.top=`${bottom}px`;''',
            # '''      destination.style.left = `${event.pageX}px`;''',
            # '''      destination.style.top = `${event.pageY}px`;''',
            '''      });''',
            '''    tooltip.addEventListener('mouseleave', () => {''',
            '''      destination.classList.remove("tooltip-active");''',
            '''      destination.classList.add("tooltip-inactive");''',
            '''      });''',
            '''    });''',
            # '''  return tooltips'''
            '''  };''',
            )

    def yield_inits(self, /):
        yield from super().yield_inits()
        yield '''initialise_tooltips();'''


class TabbedPanes(Div):

    PANE_SELECTOR_CLASS = 'pane_selector'
    PANE_SPACE_CLASS = 'pane_space'

    __slots__ = ('panes', 'pane_class', 'button_class')

    def __init__(self, /, *args, **kwargs):
        super().__init__(**kwargs)
        pane_class = self.pane_class = f"{self.identity}_pane"
        button_class = self.button_class = f"{pane_class}_button"
        panes = Div(*(
            Pane(content.title, pane_class, content) for content in args
            ), classes=(self.PANE_SPACE_CLASS,))
        pane_selector = Div(
            *(
                Button(
                    pane.tab, classes=(button_class,),
                    onclick=f'''openPane(event, '{pane_class}', '{pane.identity}')''',
                    identity=f"{self.identity}_button_{i}"
                    )
                for i, pane in enumerate(panes.contents)
                ),
            classes=(self.PANE_SELECTOR_CLASS,),
            instyles=(
                '''width: 100%;''',
                )
            )
        self.add_contents(pane_selector, panes)

    def yield_scripts(self, /):
        yield from super().yield_scripts()
        yield (
            '''function openPane(evt, paneClass, paneName) {''',
            '''  // Declare all variables''',
            '''  var i, tabcontent, tablinks;''',
            '''  // Get all elements with class=<paneClass> and hide them''',
            '''  tabcontent = document.getElementsByClassName(paneClass);''',
            '''  for (i = 0; i < tabcontent.length; i++) {''',
            '''    tabcontent[i].style.display = "none";''',
            '''    }''',
            '''  // Get all elements with class="<paneClass>_button"''',
            '''  // and remove the class "active"''',
            '''  tablinks = document.getElementsByClassName(paneClass+"_button");''',
            '''  for (i = 0; i < tablinks.length; i++) {''',
            '''    tablinks[i].className = tablinks[i].className.replace(" active", "");''',
            '''    }''',
            '''  // Show the current tab''',
            '''  // and add an "active" class to the button that opened the tab''',
            '''  document.getElementById(paneName).style.display = "block";''',
            '''  evt.currentTarget.className += " active";''',
            '''  }''',
            )

    def yield_styles(self, /):
        yield from super().yield_styles()
        yield (
            "/* Style the tab */",
            f".{self.PANE_SELECTOR_CLASS} {{",
            "  overflow: hidden;",
            # "  border: 1px solid #ccc;",
            # "  background-color: #f1f1f1;",
            # "  float:center",
            "  justify-items:center;"
            "  }",
            )
        yield (
            "/* Style the buttons that are used to open the tab content */",
            f".{self.PANE_SELECTOR_CLASS} button {{",
            "  background-color: #f1f1f1;",
            "  float: left;",
            "  border: none;",
            "  outline: none;",
            "  cursor: pointer;",
            "  padding: 14p 16px;",
            "  transition: 0.3s;",
            "  }"
            )
        yield (
            "/* Change background color of buttons on hover */",
            f".{self.PANE_SELECTOR_CLASS} button:hover {{",
            "  background-color: #ddd;",
            "  }",
            )
        yield (
            "/* Create an active/current tablink class */",
            f".{self.PANE_SELECTOR_CLASS} button.active {{",
            "  background-color: #ccc;",
            "  }",
            )
        yield (
            "/* Style the tab content */",
            f".{self.pane_class} {{",
            "  display: none;",
            "  padding: 6px 12px;",
            # "  border: 1px solid #ccc;",
            # "  border-top: none;",
            "  animation: fadeEffect 0.5s;",
            "  }"
            )
        yield (
            '''@keyframes fadeEffect {''',
            '''  from {opacity: 0;}''',
            '''  to {opacity: 1;}''',
            '''  }''',
            )


###############################################################################
###############################################################################
