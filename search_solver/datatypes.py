from typing import Counter as CounterType
from typing import List, Tuple, Dict, Union, Optional, get_args
from collections import Counter
from dataclasses import dataclass
from copy import copy

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

# 数据结构为算法服务


@dataclass
class Position:
    i: int
    j: int


@dataclass
class Shape:
    h: int
    w: int
    def __iter__(self):
        return iter((self.h, self.w))


class Color(int):
    pass


class Image:
    def __init__(self, list):
        self.list = list
        self.shape = Shape(len(list), len(list[0]))
        self.height = self.shape.h
        self.width = self.shape.w
        self.polymers: Dict[Union[FNeighbors, 'FCanCat'], Polymer] = {}
    def in_bound(self, i, j):
        return 0 <= i < self.shape.h and 0 <= j < self.shape.w
    def __getitem__(self, index):
        if isinstance(index, Position):
            index = (index.i, index.j)
        assert len(index) == 2
        if not self.in_bound(index[0], index[1]):
            raise IndexError
        return self.list[index[0]][index[1]]
    def __setitem__(self, index, value):
        if isinstance(index, Position):
            index = (index.i, index.j)
        assert len(index) == 2
        if not self.in_bound(index[0], index[1]):
            raise IndexError
        self.list[index[0]][index[1]] = value
    def __eq__(self, value) -> bool:
        return self.list == value.list
    def __repr__(self) -> str:
        s = ''
        for row in self.list:
            s += ''.join(str(x) for x in row) + '\n'
        return s[:-1]
    def copy(self):
        return Image([[x for x in row] for row in self.list])
    def plot(self, ax: plt.Axes, title):
        cmap = colors.ListedColormap(
            ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
            '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25', '#FFFFFF'])
        norm = colors.Normalize(vmin=0, vmax=10)
        ax.imshow(self.list, cmap=cmap, norm=norm)
        ax.grid(True,which='both',color='lightgrey', linewidth=0.5)
        ax.set_yticks([x-0.5 for x in range(1+self.height)])
        ax.set_xticks([x-0.5 for x in range(1+self.width)])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_title(title)


class Polymer:
    def __init__(self, pixels: List[Position]):
        super().__init__()
        self.pixels = pixels
        min_i = min(p.i for p in pixels)
        min_j = min(p.j for p in pixels)
        max_i = max(p.i for p in pixels)
        max_j = max(p.j for p in pixels)
        # if (max_i - min_i + 1) * (max_j - min_j + 1) == len(pixels):
        self.shape = Shape(max_i - min_i + 1, max_j - min_j + 1)
        self.pos = Position(min_i, min_j)


class IRNode:
    # 可以指向所有可能的信息
    def __init__(self):
        self.operands: List[IRNode] = []
        self.arguments = 0
    def get(self):
        raise NotImplementedError
    def accept(self, visitor):
        visitor.visit(self)
    def copy(self):
        new_self = copy(self)
        new_self.operands = [x.copy() if isinstance(x, IRNode) else x
                             for x in self.operands]
        return new_self

class BasicIRVisitor:
    def visit(self, pointer: IRNode):
        for operand in pointer.operands:
            operand.accept(self)

class Context:
    def __init__(self, arg_types):
        self.arg_types = arg_types
        self.context = None
    def set_context(self, context):
        self.context = context
    def __getitem__(self, index):
        return self.context[index]

class PArg(IRNode):
    def __init__(self, context: Context, index: int):
        super().__init__()
        self.context = context
        self.index = index
        self.return_type = self.context.arg_types[index]
    def get(self):
        return self.context[self.index]
    def __repr__(self):
        return f'@Arg[{self.index}]'

class Function(IRNode):
    def __init__(self):
        super().__init__()
        self.inverse_repr = False
        self.arguments = 1
        self.return_type = None
    def call(self, *args):
        raise NotImplementedError
    def get(self, x):
        if self.arguments == 1:
            return self.call(x)
        else:
            return FPartial(self, [x])

class FDefine(Function):
    def __init__(self, arguments, context: Context, body: IRNode):
        super().__init__()
        self.arguments = arguments
        self.context = context
        self.operands.append(body)
        self.return_type = body.return_type
    def call(self, *args):
        self.context.set_context(args)
        return self.operands[0].get()
    def __repr__(self):
        return f'F{{{self.operands[0]}}}'

class Apply(IRNode):
    def __init__(self, function: Function, operand: IRNode):
        super().__init__()
        self.operands.append(function)
        self.operands.append(operand)
        self.inverse_repr = False
        self.arguments = function.arguments - 1
        self.return_type = function.return_type
    def get(self, arg=None):
        if self.arguments == 0:
            return self.operands[0].get(self.operands[1].get())
        else:
            return self.operands[0].get(self.operands[1].get()).get(arg)
    def call(self, *args):
        return self.operands[0].call(self.operands[1].get(), *args)
    def __repr__(self):
        if isinstance(self.operands[0], FCompose):
            f1, f2 = self.operands[0].operands
            return repr(Apply(f1, Apply(f2, self.operands[1])))
        if self.operands[0].inverse_repr:
            return f'{self.operands[1]} {self.operands[0]}'
        else:
            return f'{self.operands[0]} {self.operands[1]}'

class FPartial(Function):
    def __init__(self, f, xs):
        super().__init__()
        self.operands.append(f)
        self.args = xs
        self.return_type = f.return_type
    def get(self, x2):
        f = self.operands[0]
        if len(self.args) + 1 == f.arguments:
            return f.call(*self.args, x2)
        else:
            return FPartial(f, self.args + [x2])
    def __repr__(self):
        return f'{self.operands[0]}({", ".join(repr(x) for x in self.args) + ", " if self.args else ""}...)'

class FCompose(Function):
    def __init__(self, function1: Function, function2: Function):
        super().__init__()
        self.operands.append(function1)
        self.operands.append(function2)
        self.arguments = function2.arguments
        self.return_type = function1.return_type
    def call(self, *args):
        return self.operands[0].get(self.operands[1].call(*args))
    def __repr__(self):
        if isinstance(self.operands[0], FCompose):
            f1, f2 = self.operands[0].operands
            return repr(FCompose(f1, FCompose(f2, self.operands[1])))
        if self.operands[0].inverse_repr:
            return f'{self.operands[1]} {self.operands[0]}'
        else:
            return f'{self.operands[0]} {self.operands[1]}'

class FInput(Function):
    def __init__(self):
        super().__init__()
        self.return_type = Image
    def call(self, sample: Tuple[Image, Image]):
        i, o = sample
        return i
    def __repr__(self):
        return f'Input Image in'
    def __eq__(self, value):
        return isinstance(value, FInput)

class FOutput(Function):
    def __init__(self):
        super().__init__()
        self.return_type = Image
    def call(self, sample: Tuple[Image, Image]):
        i, o = sample
        return o
    def __repr__(self):
        return f'Output Image in'
    def __eq__(self, value):
        return isinstance(value, FOutput)

class FColor(Function):
    def __init__(self):
        super().__init__()
        self.arguments = 2
        self.return_type = Union[CounterType[Color], Color]
    def call(self, img: Image, operand: Polymer):
        colors = Counter([img[p] for p in operand.pixels])
        if len(colors) == 1:
            return colors.popitem()[0]
        else:
            return colors
    def __eq__(self, value):
        return isinstance(value, FColor)
    def __repr__(self):
        return f'Color of'

class FShape(Function):
    def __init__(self):
        super().__init__()
        self.return_type = Shape
    def call(self, operand: Image):
        return operand.shape
    def __eq__(self, value):
        return isinstance(value, FShape)
    def __repr__(self):
        return f'Shape of'

class FShapeScale(Function):
    def __init__(self, scale_h, scale_w):
        super().__init__()
        self.scale_h = scale_h
        self.scale_w = scale_w
        self.return_type = Shape
    def call(self, operand: Shape):
        return Shape(operand.h * self.scale_h, operand.w * self.scale_w)
    def __eq__(self, value):
        return isinstance(value, FShapeScale) and self.scale_h == value.scale_h and self.scale_w == value.scale_w
    def __repr__(self):
        return f'Scale {self.scale_h}x{self.scale_w} of'

class PConstant(IRNode):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.return_type = type(value)
    def get(self):
        return self.value
    def __eq__(self, value):
        return isinstance(value, PConstant) and self.value == value.value
    def __repr__(self):
        return f'{self.value}'

class FConstant(Function):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.return_type = type(value)
    def call(self, _):
        return self.value
    def __eq__(self, value):
        return isinstance(value, FConstant) and self.value == value.value
    def __repr__(self):
        return f'{self.value}'

class FPolymers(Function):
    def __init__(self, relation: Union['FNeighbors', 'FCanCat']):
        super().__init__()
        self.relation = relation
        self.return_type = List[Polymer]
    def call(self, img: Image):
        return img.polymers[self.relation]
    def __repr__(self):
        return f'Polymers of'

class FMap(Function):
    def __init__(self, f: Function):
        super().__init__()
        self.operands.append(f)
        self.return_type = f.return_type
    def call(self, xs: List):
        return [self.operands[0].get(x) for x in xs]
    def __repr__(self):
        return f'Map {self.operands[0]} over'

class FNot(Function):
    def __init__(self):
        super().__init__()
        self.return_type = bool
    def call(self, x):
        return not x
    def __repr__(self):
        return f'not'

class FEqual(Function):
    def __init__(self):
        super().__init__()
        self.inverse_repr = True
        self.return_type = bool
        self.arguments = 2
    def call(self, x1, x2):
        return x1 == x2
    def __repr__(self):
        return f'is Equal to'

class PPick(IRNode):
    def __init__(self, operand: IRNode, picker: Function):
        super().__init__()
        self.operands.append(operand)
        self.operands.append(picker)
        self.return_type = get_args(operand.return_type)[0]
    def get(self):
        xs = self.operands[0].get()
        picked_xs = [x for x in xs if self.operands[1].get(x)]
        if len(picked_xs) != 1:
            print(f'Warning: {len(picked_xs)} values picked from {self.operands[0]} that {self.operands[1]}')
        return picked_xs[0]
    def __repr__(self):
        return f'One that picked from {self.operands[0]} that {self.operands[1]}'

class FMost(Function):
    def __init__(self, strict: bool):
        super().__init__()
        self.strict = strict
        if strict:
            self.return_type = int
        else:
            self.return_type = List[int]
    def call(self, xs: List):
        counter = Counter(xs)
        _, num = counter.most_common(1)[0]
        picked = [x for x, n in counter.items() if n == num]
        if self.strict:
            assert len(picked) == 1
            return picked[0]
        return picked
    def __repr__(self):
        return f'Most {"one" if self.strict else "nums"} in'

class FLeast(Function):
    def __init__(self, strict: bool):
        super().__init__()
        self.strict = strict
        if strict:
            self.return_type = int
        else:
            self.return_type = List[int]
    def call(self, xs: List):
        counter = Counter(xs)
        _, num = counter.most_common()[-1]
        picked = [x for x, n in counter.items() if n == num]
        if self.strict:
            assert len(picked) == 1
            return picked[0]
        return picked
    def __repr__(self):
        return f'Least {"one" if self.strict else "nums"} in'

class FNeighbors(Function):
    def __init__(self, raw=True, col=True, diag=False, same_color=True):
        super().__init__()
        self.raw = raw
        self.col = col
        assert raw or col
        self.diag = diag
        assert not diag or (raw and col)
        assert same_color

        self.return_type = List[Position]
        self.arguments = 2
    def __eq__(self, value):
        return isinstance(value, FNeighbors) and self.raw == value.raw and \
            self.col == value.col and self.diag == value.diag
    def __hash__(self):
        return hash((self.raw, self.col, self.diag))
    def call(self, img: Image, p: Position):
        i, j = p.i, p.j
        positions = []
        neighbors = []
        if self.raw:
            neighbors += [(i, j-1), (i, j+1)]
        if self.col:
            neighbors += [(i-1, j), (i+1, j)]
        if self.diag:
            neighbors += [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
        for ii, jj in neighbors:
            if img.in_bound(ii, jj) and img[i, j] == img[ii, jj]:
                positions.append(Position(ii, jj))
        return positions

class FCanCat(Function):
    def __init__(self, cat_type: str, source_polymer_type: Union[FNeighbors, 'FCanCat']):
        super().__init__()
        self.cat_type = cat_type
        self.source_polymer_type = source_polymer_type
        self.return_type = bool
        self.arguments = 2
    def __eq__(self, value):
        return isinstance(value, FCanCat) and self.cat_type == value.cat_type and \
            self.source_polymer_type == value.source_polymer_type
    def __hash__(self):
        return hash((self.cat_type, self.source_polymer_type))
    def can_cat_vertical(self, p1: Polymer, p2: Polymer):
        return p1.shape.w == p2.shape.w and p1.pos.j == p2.pos.j and \
            (p1.pos.i + p1.shape.h == p2.pos.i or p2.pos.i + p2.shape.h == p1.pos.i)
    def can_cat_horizontal(self, p1: Polymer, p2: Polymer):
        return p1.shape.h == p2.shape.h and p1.pos.i == p2.pos.i and \
            (p1.pos.j + p1.shape.w == p2.pos.j or p2.pos.j + p2.shape.w == p1.pos.j)
    def can_cat_inner(self, p1: Polymer, p2: Polymer):
        return (p1.pos.i <= p2.pos.i and p1.pos.j <= p2.pos.j and \
                p1.pos.i + p1.shape.h >= p2.pos.i + p2.shape.h and p1.pos.j + p1.shape.w >= p2.pos.j + p2.shape.w) or \
               (p2.pos.i <= p1.pos.i and p2.pos.j <= p1.pos.j and \
                p2.pos.i + p2.shape.h >= p1.pos.i + p1.shape.h and p2.pos.j + p2.shape.w >= p1.pos.j + p1.shape.w)
    def call(self, img: Image, p1: Polymer, p2: Polymer):
        same_color = FColor().call(img, p1) == FColor().call(img, p2)
        if self.cat_type == 'vertical':
            can_cat = self.can_cat_vertical(p1, p2)
        elif self.cat_type == 'horizontal':
            can_cat = self.can_cat_horizontal(p1, p2)
        elif self.cat_type == 'inner':
            can_cat = self.can_cat_inner(p1, p2)
        else:
            raise ValueError(f'Invalid cat_type: {self.cat_type}')
        return can_cat and same_color
