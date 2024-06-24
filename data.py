import os
import json
from typing import Dict, Set

class Image:
    def __init__(self, list):
        self.list = list
        self.shape = (len(list), len(list[0]))
    def color_set(self) -> Set[int]:
        return set(x for row in self.list for x in row)
    def __getitem__(self, index):
        assert len(index) == 2
        if index[0] >= self.shape[0] or index[1] >= self.shape[1]:
            return 0
        if index[0] < 0 or index[1] < 0:
            return 0
        return self.list[index[0]][index[1]]
    def __eq__(self, value) -> bool:
        return self.list == value.list
    def __repr__(self) -> str:
        s = ''
        for row in self.list:
            s += ''.join(str(x) for x in row) + '\n'
        return s[:-1]
    @staticmethod
    def generate(f, shape):
        img = [[f(i, j) for j in range(shape[1])]
               for i in range(shape[0])]
        return Image(img)

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
