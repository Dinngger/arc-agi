from dataclasses import dataclass
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


class Color(int):
    pass


class Image:
    def __init__(self, list):
        self.list = list
        self.shape = Shape(len(list), len(list[0]))
        self.height = self.shape.h
        self.width = self.shape.w
    def in_bound(self, i, j):
        return 0 <= i < self.shape.h and 0 <= j < self.shape.w
    def __getitem__(self, index):
        assert len(index) == 2
        if not self.in_bound(index[0], index[1]):
            raise IndexError
        return self.list[index[0]][index[1]]
    def __setitem__(self, index, value):
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
