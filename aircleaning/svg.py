###############################################################################
''''''
###############################################################################


import abc
from collections import UserList
import itertools as _itertools
import os as _os
import colorsys

import numpy as np
from scipy.spatial.transform import Rotation

from .html import Normal as _Normal, Void as _Void


class Transform:

    __slots__ = ('_panval', '_tiltval', '_focus', '_transform')

    def __init__(self, pan=0, tilt=0, focus=(0, 0, 0)):
        self.panval, self.tiltval = pan, tilt
        self._focus = np.array(focus, dtype=float)

    @property
    def panval(self, /):
        return self._panval

    @panval.setter
    def panval(self, val, /):
        self._panval = float(val)
        try:
            del self._transform
        except AttributeError:
            pass

    @property
    def tiltval(self, /):
        return self._tiltval

    @tiltval.setter
    def tiltval(self, val, /):
        self._tiltval = float(val)
        try:
            del self._transform
        except AttributeError:
            pass

    def pan(self, val, /):
        self.panval += val

    def tilt(self, val, /):
        self.tiltval += val

    @property
    def focus(self, /):
        return self._focus

    @focus.setter
    def focus(self, val, /):
        self._focus[...] = val

    @property
    def transform(self, /):
        try:
            return self._transform
        except AttributeError:
            transform = self._transform = Rotation.from_euler(
                'zx', (-self.panval, -self.tiltval), degrees=True
                )
            return transform

    def __call__(self, arr, /):
        return self.transform.apply(np.array(arr) - self.focus)


class Projection:

    __slots__ = ('_width', '_height', '_scaleval')

    def __init__(self, width=424, height=300, scale=1):
        self.width, self.height, self.scaleval = width, height, scale

    @property
    def width(self, /):
        return self._width

    @width.setter
    def width(self, val, /):
        self._width = int(val)

    @property
    def height(self, /):
        return self._height

    @height.setter
    def height(self, val, /):
        self._height = int(val)

    @property
    def scale(self, /):
        return self._scaleval

    @scale.setter
    def scaleval(self, val, /):
        self._scaleval = float(val)

    def scale(self, val, /):
        self.scaleval *= val

    def __call__(self, arg, /):
        arr = np.array(arg) * self.scaleval
        arr[:, 0] += self.width / 2
        arr[:, 1] = self.height / 2 - arr[:, 1]
        return arr[:, :-1]


class View:

    __slots__ = ('_projection', '_transform')

    def __init__(self, projection, transform):
        self._projection, self._transform = projection, transform

    @property
    def projection(self, /):
        return self._projection

    @property
    def transform(self, /):
        return self._transform

    def __call__(self, entity, /):
        return self.projection(self.transform(entity))


class SVG(_Normal):

    element_type_name = 'svg'

    __slots__ = ()

    def yield_svg_boilerplate(self, /):
        yield 0, '''<?xml version="1.0" encoding="UTF-8"?>'''

    def yield_attributes(self, /):
        yield 'xmlns', '''"http://www.w3.org/2000/svg"'''

    def _repr_svg_(self, /):
        standard = self.standard_indent
        out = []
        for indent, text in _itertools.chain(
                self.yield_svg_boilerplate(),
                self.yield_lines(),
                ):
            out.append(indent*standard)
            out.append(text)
            out.append('\n')
        return ''.join(out)

    def save_svg(self, /, name, path='.'):
        with open(_os.path.join(path, name) + '.svg', mode='w') as file:
            file.write(self._repr_svg_())


class Canvas(SVG):

    __slots__ = ('_graphics', '_view',)

    def __init__(self, view = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if view is None:
            view = View(Projection(), Transform())
        self._view = view
        self._graphics = []

    @property
    def graphics(self, /):
        return tuple(self._graphics)

    def add(self, obj, /, *objs):
        if isinstance(obj, Compound):
            self._graphics.extend(obj.graphics)
        else:
            self._graphics.append(obj)
        if objs:
            for obj in objs:
                self.add(obj)

    @property
    def view(self, /):
        return self._view

    @property
    def projection(self, /):
        return self.view.projection

    @property
    def transform(self, /):
        return self.view.transform

    def yield_attributes(self, /):
        yield from super().yield_attributes()
        yield 'width', f'"{self.projection.width}"'
        yield 'height', f'"{self.projection.height}"'
        yield 'style', f'"background-color:white"'

    def _yield_lines_(self, /):
        for graphic in self.graphics:
            typ, dct = graphic.draw(self.view)
            yield 0, f"<{typ} {' '.join(map('='.join, dct.items()))} />"


class Graphic:

    __slots__ = ()

    @abc.abstractmethod
    def __array__(self, /):
        raise NotImplementedError        

    @abc.abstractmethod
    def draw(self, view, /):
        raise NotImplementedError


class Flat(Graphic):

    element_type_name = 'polygon'

    _omap = {
        'xy': (0, 1, 2),
        'xz': (0, 2, 1),
        'yz': (1, 2, 0),
        }

    __slots__ = ('_u0', '_u1', '_v0', '_v1', '_orientation', '_fill', '_fixed')

    def __init__(self, orientation, u0, u1, v0, v1, fixed, fill='black'):
        self.orientation = str(orientation)
        self.fill = fill
        self.u0, self.u1, self.v0, self.v1, self.fixed = u0, u1, v0, v1, fixed

    @property
    def orientation(self, /):
        return self._orientation

    @orientation.setter
    def orientation(self, val, /):
        val = str(val)
        if val not in self._omap:
            raise ValueError(val)
        self._orientation = val

    @property
    def fill(self, /):
        return self._fill

    @fill.setter
    def fill(self, val, /):
        self._fill = str(val)

    @property
    def u0(self, /):
        return self._u0

    @u0.setter
    def u0(self, val, /):
        self._u0 = float(val)

    @property
    def u1(self, /):
        return self._u1

    @u1.setter
    def u1(self, val, /):
        self._u1 = float(val)

    @property
    def v0(self, /):
        return self._v0

    @v0.setter
    def v0(self, val, /):
        self._v0 = float(val)

    @property
    def v1(self, /):
        return self._v1

    @v1.setter
    def v1(self, val, /):
        self._v1 = float(val)

    @property
    def fixed(self, /):
        return self._fixed

    @fixed.setter
    def fixed(self, val, /):
        self._fixed = float(val)    

    @property
    def ul(self, /):
        return self.u1 - self.u0

    @ul.setter
    def ul(self, val, /):
        mid = (self.u0 + self.u1) / 2
        val = val / 2
        self.u0 = mid - val
        self.u1 = mid + val

    @property
    def vl(self, /):
        return self.v1 - self.v0

    @vl.setter
    def vl(self, val, /):
        mid = (self.v0 + self.v1) / 2
        val = val / 2
        self.v0 = mid - val
        self.v1 = mid + val

    def uscale(self, val, /):
        self.ul *= val

    def vscale(self, val, /):
        self.vl *= val

    def scale(self, val):
        self.uscale(val)
        self.vscale(val)

    @property
    def uc(self, /):
        return (self.u0 + self.u1) / 2

    @uc.setter
    def uc(self, val, /):
        half = self.ul / 2
        self.u0 = val - half
        self.u1 = val + half

    @property
    def vc(self, /):
        return (self.v0 + self.v1) / 2

    @vc.setter
    def vc(self, val, /):
        half = self.vl / 2
        self.v0 = val - half
        self.v1 = val + half

    def __array__(self, /):
        out = np.empty((4, 3), dtype=float)
        ud, vd, fd = self._omap[self.orientation]
        out[:, ud] = (self.u0, self.u0, self.u1, self.u1)
        out[:, vd] = (self.v0, self.v1, self.v1, self.v0)
        out[:, fd] = self.fixed
        return out

    def draw(self, view, /):
        arr = view(self)
        pointstr = ' '.join(f"{x},{y}" for x, y in arr)
        return (
            'polygon',
            dict(fill=f'"{self.fill}"', points=f'"{pointstr}"'),
            )


class Compound:

    __slots__ = ()

    @property
    @abc.abstractmethod
    def graphics(self, /) -> tuple:
        raise NotImplementedError


class Box(Compound):

    __slots__ = (
        '_lv', '_rv', '_nv', '_fv', '_bv', '_tv',
        '_left', '_right', '_near', '_far', '_bottom', '_top',
        )

    def __init__(self, left, right, near, far, bottom, top):
        self.lv, self.rv, self.nv, self.fv, self.bv, self.tv = \
            (left, right, near, far, bottom, top)
        self._left, self._right, self._near, self._far, self._bottom, self._top = (
            self._make_flat(side) for side in (
                'left', 'right', 'near', 'far', 'bottom', 'top'
                )
            )

    @property
    def lv(self, /):
        return self._lv

    @lv.setter
    def lv(self, val, /):
        self._lv = float(val)

    @property
    def rv(self, /):
        return self._rv

    @rv.setter
    def rv(self, val, /):
        self._rv = float(val)

    @property
    def nv(self, /):
        return self._nv

    @nv.setter
    def nv(self, val, /):
        self._nv = float(val)

    @property
    def fv(self, /):
        return self._fv

    @fv.setter
    def fv(self, val, /):
        self._fv = float(val)

    @property
    def bv(self, /):
        return self._bv

    @bv.setter
    def bv(self, val, /):
        self._bv = float(val)

    @property
    def tv(self, /):
        return self._tv

    @tv.setter
    def tv(self, val, /):
        self._tv = float(val)

    def _make_flat(self, side, /, **kwargs):
        if side in ('bottom', 'top'):
            orientation = 'xy'
            vals = self.lv, self.rv, self.nv, self.fv
        elif side in ('near', 'far'):
            orientation = 'xz'
            vals = self.lv, self.rv, self.bv, self.tv
        elif side in ('left', 'right'):
            orientation = 'yz'
            vals = self.nv, self.fv, self.bv, self.tv
        else:
            raise ValueError(side)
        return Flat(orientation, *vals, getattr(self, side[0]+'v'))

    @property
    def breadth(self, /):
        return self.rv - self.lv

    @property
    def depth(self, /):
        return self.fv - self.nv

    @property
    def height(self, /):
        return self.tv - self.bv

    @property
    def centre(self, /):
        return (
            (self.lv + self.breadth / 2),
            (self.nv + self.depth / 2),
            (self.bv + self.height / 2),
            )

    @property
    def left(self, /):
        return self._left

    @property
    def right(self, /):
        return self._right

    @property
    def near(self, /):
        return self._near

    @property
    def far(self, /):
        return self._far

    @property
    def bottom(self, /):
        return self._bottom

    @property
    def top(self, /):
        return self._top

    @property
    def graphics(self, /):
        return (self.left, self.right, self.near, self.far, self.bottom, self.top)


class Hollow(Box):

    __slots__ = ()

    @property
    def floor(self, /):
        return self.bottom

    @property
    def back(self, /):
        return self.far

    @property
    def side(self, /):
        return self.right

    @property
    def graphics(self, /):
        return (self.floor, self.back, self.side)


class Solid(Box):

    __slots__ = ()

    @property
    def front(self, /):
        return self.near

    @property
    def side(self, /):
        return self.left

    @property
    def roof(self, /):
        return self.top

    @property
    def graphics(self, /):
        return (self.front, self.side, self.roof)


# class Cube(Solid):

#     __slots__ = ()

#     def __init__(self, x, y, width=0.4, height=1.7):
#         hwidth = width / 2
#         super().__init__(x-hwidth, x+hwidth, y-hwidth, y+hwidth, 0, height)
#         self.front.fill = 'antiquewhite'
#         self.side.fill = 'beige'
#         self.roof.fill = 'bisque'


class Person(Compound):

    __slots__ = ('_graphics',)

    _CROTCH_HEIGHT = 0.4
    _LEG_WIDTH = 0.8
    _ARM_WIDTH = 0.7
    _SHOULDER_WIDTH = 0.1
    _HEAD_HEIGHT = 0.2
    _HEAD_WIDTH = 0.5
    _NECK_LENGTH = 0.1
    _NECK_WIDTH = 0.6

    def __init__(self, x, y, width=0.3, height=1.7, fill='LightGreen'):
        hwidth = width / 2
        lside = x-hwidth
        rside = x+hwidth
        arm_thickness = hwidth*self._ARM_WIDTH
        lshoulder = lside - hwidth * self._SHOULDER_WIDTH
        rshoulder = rside + hwidth * self._SHOULDER_WIDTH
        crotch_height = height * self._CROTCH_HEIGHT
        head_height = height * (1 - self._HEAD_HEIGHT)
        head_width = hwidth * self._HEAD_WIDTH
        neck_width = head_width * self._NECK_WIDTH
        lleg = Flat(
            'xz',
            x-hwidth, x-hwidth*(1-self._LEG_WIDTH),
            0, crotch_height*1.01,
            y, fill,
            )
        rleg = Flat(
            'xz',
            x+hwidth, x+hwidth*(1-self._LEG_WIDTH),
            0, crotch_height*1.01,
            y, fill,
            )
        larm = Flat(
            'xz',
            lshoulder-arm_thickness, lshoulder,
            crotch_height, head_height,
            y, fill,
            )
        rarm = Flat(
            'xz',
            rshoulder, rshoulder+arm_thickness,
            crotch_height, head_height,
            y, fill,
            )
        shoulders = Flat(
            'xz',
            lshoulder, rshoulder,
            head_height - arm_thickness, head_height,
            y, fill,
            )
        torso = Flat(
            'xz',
            x-hwidth, x+hwidth,
            crotch_height, head_height,
            y, fill,
            )
        head = Flat(
            'xz',
            x-head_width, x+head_width,
            head_height+(height-head_height)*self._NECK_LENGTH, height,
            y, fill,
            )
        neck = Flat(
            'xz',
            x-neck_width, x+neck_width,
            head_height, height,
            y, fill,
            )
        self._graphics = (
            lleg, rleg, larm, rarm, shoulders, torso, head, neck
            )
        # super().__init__(x-hwidth, x+hwidth, y-hwidth, y+hwidth, 0, height)
        super().__init__()

    @property
    def graphics(self, /):
        return self._graphics


class Room(Hollow):

    __slots__ = ('_door',)

    def __init__(self, breadth, depth, height):
        super().__init__(0, breadth, 0, depth, 0, height)
        self.back.fill = 'steelblue'
        self.side.fill = 'lightskyblue'
        self.floor.fill = 'lightblue'
        self._door = ...

    @property
    def door(self, /):
        return self._door


def html_hsl(hue, saturation, lightness, /):
    return f"hsl({hue*360},{saturation*100}%,{lightness*100}%)"


def draw_scene(
        length=6, width=4, height=2.7, persons=1, activity=0, windows=2, doors=1, mech=True,
        size=1, scale=1, seed=0,
        **kwargs,
        ):
    canvas = Canvas(**kwargs)
    canvas.projection.width *= size
    canvas.projection.height *= size
    canvas.projection.scale(size)
    room = Room(length, width, height)
    canvas.add(room)
    floor, wall0, wall1 = room.bottom, room.far, room.right
    door_spacing = width / (doors + 1)
    for i in range(1, doors + 1):
        window = Flat(
            'yz',
            room.fv-i*door_spacing-0.3, room.fv-i*door_spacing+0.3,
            room.bv, room.bv+1.9, room.rv, fill='white',
            )
        canvas.add(window)
    # door = Flat('yz', wall1.uc-0.3, wall1.uc+0.3, 0, 2, room.rv, fill='white')
    # canvas.add(door)
    window_spacing = length / (windows + 1)
    for i in range(1, windows + 1):
        window = Flat(
            'xz',
            room.lv+i*window_spacing-0.25, room.lv+i*window_spacing+0.25,
            room.bv+0.8, room.bv+1.6, room.fv, fill='white',
            )
        canvas.add(window)
    if mech:
        mechbox = Solid(wall0.u1-0.5, wall0.u1, wall1.u1-0.5, wall1.u1, wall0.v1-0.7, wall0.v1-0.2)
        mechbox.front.fill = 'grey'
        mechbox.side.fill = 'lightgrey'
        mechbox.roof.fill = 'darkgrey'
        canvas.add(mechbox)
    rng = np.random.default_rng(seed)
    coords = []
    figures = []
    for _ in range(persons):
        for __ in range(100):
            ucoord = floor.u0 + 1 + rng.random() * (floor.ul - 2)
            vcoord = floor.v0 + 1 + rng.random() * (floor.vl - 2)
            if not any(
                    abs(ucoord-uval)<1 and abs(vcoord-vval)<1
                    for (uval, vval) in coords
                    ):
                break
        coords.append((ucoord, vcoord))
        depth = (vcoord - floor.v0) / floor.vl
        fill = html_hsl(
            (0.8, 0.9, 1.0)[activity],
            0.5,
            depth / 2 + 1/3
            )
        # rgb = {0: (0), 1: (), 2: ()}
        # fill = f"rgb({','.join(map(str, rgb))})"
        person = Person(ucoord, vcoord, fill=fill)
        figures.append((depth, person))
    figures.sort(key=lambda x: -x[0])
    for _, figure in figures:
        canvas.add(figure)
    canvas.transform.focus = room.centre
    canvas.transform.pan(-30)
    canvas.transform.tilt(60)
    canvas.projection.scale(50)
    canvas.projection.scale(scale)
    return canvas


###############################################################################
###############################################################################
