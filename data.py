import os
import json
from typing import Dict, Set

class Image:
    def __init__(self, list):
        self.list = list
        self.shape = (len(list), len(list[0]))
        self.color_count()
    def color_count(self) -> Set[int]:
        color_count = {}
        for row in self.list:
            for x in row:
                if x not in color_count:
                    color_count[x] = 0
                color_count[x] += 1
        most_color = max(color_count, key=color_count.get)
        self.background_color = 0 if 0 in color_count else most_color   # maybe just try the two choices
        if self.shape[0] <= 3 or self.shape[1] <= 3:
            self.background_color = 0
        self.color_set = set(color_count.keys())
    def copy(self):
        return Image([[x for x in row] for row in self.list])
    def subimage(self, top, left, bottom, right):
        sub = Image([[self.list[i][j] for j in range(left, right+1)] for i in range(top, bottom+1)])
        return sub
    def pattern3x3(self, i, j):
        pattern = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                pattern.append(self[i+x, j+y])
        return pattern
    def in_bound(self, i, j):
        return 0 <= i < self.shape[0] and 0 <= j < self.shape[1]
    def __getitem__(self, index):
        assert len(index) == 2
        if not self.in_bound(index[0], index[1]):
            return self.background_color
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
    def self_generate(self, f):
        img = [[f(self, i, j) for j in range(self.shape[1])]
               for i in range(self.shape[0])]
        return Image(img)
    @staticmethod
    def generate(f, shape):
        img = [[f(i, j) for j in range(shape[1])]
               for i in range(shape[0])]
        return Image(img)
    @staticmethod
    def zeros(shape):
        return Image.generate(lambda i, j: 0, shape)

class Sample:
    def __init__(self, s):
        self.input = Image(s['input'])
        self.output = Image(s['output'])

class Data:
    def __init__(self, data):
        self.data = data
        self.train = [Sample(s) for s in data['train']]
        self.test = [Sample(s) for s in data['test']]

def get_data(train=True) -> Dict[str, Data]:
    path = f'../ARC-AGI/data/{"training" if train else "evaluation"}'
    data = {}
    for fn in os.listdir(path):
        with open(f'{path}/{fn}') as f:
            data[fn.rstrip('.json')] = Data(json.load(f))
    return data


if __name__ == '__main__':
    data = get_data(train=True)['ce602527']
    for s in data.train:
        print(s.input.background_color)
