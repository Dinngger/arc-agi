import os
import json
from typing import List

class Node:
    def __init__(self, contains: List['Node']=[]):
        self.contains = contains
        for c in contains:
            c.belong_to.append(self)
        self.belong_to = []
        self.related_to = []
    def __eq__(self, value: 'Node'):
        return self.contains == value.contains
    def __repr__(self) -> str:
        s = f'{self.__class__.__name__}('
        s += ', '.join(str(c) for c in self.contains)
        s += ')'
        return s

class Rule(Node):
    def __init__(self, condition, action):
        super().__init__()

class Color(Node):
    def __init__(self, c: int):
        super().__init__()
        self.c = c
    def __eq__(self, value: 'Color'):
        return self.c == value.c

class Pixel(Node):
    def __init__(self, i, j, c):
        super().__init__([Color(c)])
        self.i = i
        self.j = j

class Image(Node):
    def __init__(self, pixels: List[List[int]]):
        self.height = len(pixels)
        self.width = len(pixels[0])
        for row in pixels:
            assert len(row) == self.width
        objs = []
        for i in range(self.height):
            for j in range(self.width):
                objs.append(Pixel(i, j, pixels[i][j]))
        super().__init__(objs)
    def in_bound(self, i, j):
        return 0 <= i < self.height and 0 <= j < self.width
    def __getitem__(self, index) -> Pixel:
        assert len(index) == 2
        if isinstance(index[0], slice) or isinstance(index[1], slice):
            raise NotImplementedError("Slicing not supported yet")
            return Image([row[index[1]] for row in self.list[index[0]]])
        if not self.in_bound(index[0], index[1]):
            raise IndexError(f"Index {index} out of bound")
        return self.contains[0][index[0] * self.width + index[1]]
    def __repr__(self) -> str:
        s = '\n'
        for i in range(self.height):
            for j in range(self.width):
                s += str(self.contains[i * self.width + j].contains[0].c)
            s += '\n'
        return s[:-1]

def image_compressor(img: Image):
    pass

class TrainSample(Node):
    def __init__(self, s):
        input = Image(s['input'])
        output = Image(s['output'])
        super().__init__([input, output])

class TestSample(Node):
    def __init__(self, s):
        input = Image(s['input'])
        super().__init__([input])
        self.output = Image(s['output'])

class Data(Node):
    def __init__(self, k, data):
        trains = [TrainSample(s) for s in data['train']]
        tests = [TestSample(s) for s in data['test']]
        super().__init__(trains + tests)
        self.k = k

def load_data(path, k) -> Data:
    with open(f'{path}/{k}.json') as f:
        data = Data(k, json.load(f))
    return data

def load_datas(path) -> List[Data]:
    datas = []
    for fn in os.listdir(path):
        datas.append(load_data(path, fn.rstrip('.json')))
    return datas

# 所有图像进入感知舞台，提取单像素相似性
# 浅层鬼提取信息，提取浅层相似性
# 高层鬼提取信息，提取高层相似性

# 最显著的相似性，进行成分决策。验证因果性而非相关性。
# 决策完剩余部分回到前述步骤。


# 直觉 - 严谨： https://cul.sina.com.cn/o/2006-01-26/1030152927.html?from=wap
