from typing import List, Tuple, Optional, get_args
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
        self.polymers: List[Polymer] = []
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
    def __init__(self, color: Color, pixels: List[Position], relation):
        super().__init__()
        self.color = color
        self.pixels = pixels
        self.relation = relation
        min_i = min(p.i for p in pixels)
        min_j = min(p.j for p in pixels)
        max_i = max(p.i for p in pixels)
        max_j = max(p.j for p in pixels)
        if (max_i - min_i + 1) * (max_j - min_j + 1) == len(pixels):
            self.shape = Shape(max_i - min_i + 1, max_j - min_j + 1)
        else:
            self.shape = None


class Pointer:
    # 可以指向所有可能的信息
    def __init__(self):
        self.operands = []
    def get_value(self):
        raise NotImplementedError
    def accept(self, visitor):
        visitor.visit(self)
    def copy(self):
        new_self = copy(self)
        new_self.operands = [x.copy() if isinstance(x, Pointer) else x
                             for x in self.operands]
        return new_self

class BasicPointerVisitor:
    def visit(self, pointer: Pointer):
        for operand in pointer.operands:
            operand.accept(self)

class Function(Pointer):
    def __init__(self):
        super().__init__()
        self.inverse_repr = False
        self.return_type = None

class PApply(Pointer):
    def __init__(self, function: Function, operand: Pointer):
        super().__init__()
        self.operands.append(function)
        self.operands.append(operand)
        self.return_type = function.return_type
    def get_value(self):
        return self.operands[0].get_value(self.operands[1].get_value())
    def __repr__(self):
        if isinstance(self.operands[0], FCompose):
            f1, f2 = self.operands[0].operands
            return repr(PApply(f1, PApply(f2, self.operands[1])))
        if self.operands[0].inverse_repr:
            return f'{self.operands[1]} {self.operands[0]}'
        else:
            return f'{self.operands[0]} {self.operands[1]}'

class FCompose(Function):
    def __init__(self, function1: Function, function2: Function):
        super().__init__()
        self.operands.append(function1)
        self.operands.append(function2)
        self.return_type = function1.return_type
    def get_value(self, x):
        return self.operands[0].get_value(self.operands[1].get_value(x))
    def __repr__(self):
        if isinstance(self.operands[0], FCompose):
            f1, f2 = self.operands[0].operands
            return repr(PApply(f1, PApply(f2, self.operands[1])))
        if self.operands[0].inverse_repr:
            return f'{self.operands[1]} {self.operands[0]}'
        else:
            return f'{self.operands[0]} {self.operands[1]}'

class PAnySample(Pointer):
    # 常量，代表所有样本，可用于任意样本。
    def __init__(self):
        super().__init__()
        # self.return_type = Sample
    def get_value(self):
        raise ValueError('No sample is set.')
    def __eq__(self, other):
        return isinstance(other, PAnySample)
    def __repr__(self):
        return 'the Sample'

class UseSample(BasicPointerVisitor):
    def __init__(self, sample: List[Tuple[Image, Image]]):
        super().__init__()
        self.sample = sample
    def visit(self, pointer: Pointer):
        if isinstance(pointer, PAnySample):
            raise ValueError('give me its father.')
        for i in range(len(pointer.operands)):
            if isinstance(pointer.operands[i], PAnySample):
                pointer.operands[i] = PSample(self.sample)
        super().visit(pointer)

def use_sample(pointer: Pointer, sample: List[Tuple[Image, Image]]):
    new_pointer = pointer.copy()
    UseSample(sample).visit(new_pointer)
    return new_pointer

class PSample(Pointer):
    def __init__(self, sample):
        super().__init__()
        self.sample = sample
    def get_value(self):
        return self.sample
    def __eq__(self, other):
        return isinstance(other, PSample) and self.sample is other.sample

class PImage(Pointer):
    def __init__(self):
        super().__init__()
        self.return_type = Image

class PInput(PImage):
    def __init__(self, p_sample: PAnySample):
        super().__init__()
        self.operands.append(p_sample)
    def get_value(self):
        i, o = self.operands[0].get_value()
        return i
    def __repr__(self):
        return f'Input Image in {self.operands[0]}'
    def __eq__(self, value):
        return isinstance(value, PInput) and self.operands[0] == value.operands[0]

class POutput(PImage):
    def __init__(self, p_sample: PAnySample):
        super().__init__()
        self.operands.append(p_sample)
    def get_value(self):
        i, o = self.operands[0].get_value()
        return o
    def __repr__(self):
        return f'Output Image in {self.operands[0]}'
    def __eq__(self, value):
        return isinstance(value, POutput) and self.operands[0] == value.operands[0]

class FColor(Function):
    def __init__(self):
        super().__init__()
        self.return_type = Color
    def get_value(self, operand: Polymer):
        return operand.color
    def __eq__(self, value):
        return isinstance(value, FColor)
    def __repr__(self):
        return f'Color of'

class FShape(Function):
    def __init__(self):
        super().__init__()
        self.return_type = Shape
    def get_value(self, operand: Image):
        return operand.shape
    def __eq__(self, value):
        return isinstance(value, FShape)
    def __repr__(self):
        return f'Shape of'

class PConstant(Pointer):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.return_type = type(value)
    def get_value(self):
        return self.value
    def __eq__(self, value):
        return isinstance(value, PConstant) and self.value == value.value
    def __repr__(self):
        return f'{self.value}'

class PList(Pointer):
    def __init__(self):
        super().__init__()

class PPolymers(PList):
    def __init__(self, operand: PImage):
        super().__init__()
        self.operands.append(operand)
        self.return_type = List[Polymer]
        # self.relation = relation
    def get_value(self):
        return self.operands[0].get_value().polymers
    def __repr__(self):
        return f'Polymers of {self.operands[0]}'

class PMap(PList):
    def __init__(self, operand: PList, function: Function):
        super().__init__()
        self.operands.append(operand)
        self.operands.append(function)
        self.return_type = List[function.return_type]
    def get_value(self):
        return [self.operands[1].get_value(x)
                for x in self.operands[0].get_value()]

class FEqual(Function):
    def __init__(self, operand):
        super().__init__()
        self.inverse_repr = True
        self.return_type = bool
        self.operands.append(operand)
    def get_value(self, other):
        return self.operands[0].get_value() == other
    def __repr__(self):
        return f'is Equal to {self.operands[0]}'

class PPick(Pointer):
    def __init__(self, operand: PList, picker: Function):
        super().__init__()
        self.operands.append(operand)
        self.operands.append(picker)
        self.return_type = get_args(operand.return_type)[0]
    def get_value(self):
        xs = self.operands[0].get_value()
        picked_xs = [x for x in xs if self.operands[1].get_value(x)]
        assert len(picked_xs) == 1
        return picked_xs[0]
    def __repr__(self):
        return f'One that picked from {self.operands[0]} that {self.operands[1]}'
