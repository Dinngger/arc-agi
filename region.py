import numpy as np
from typing import Tuple
from dataclasses import dataclass


def easy_region(img):
    def get_neighbour(x, y):
        neighbour = []
        for i in range(x-1, x+2):
            if 0 <= i < img.shape[0]:
                for j in range(y-1, y+2):
                    if 0 <= j < img.shape[1]:
                        if (i, j) != (x, y):
                            neighbour.append((i, j))
        return neighbour
    region = -np.ones(img.shape, int)
    current_region = -1
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if region[x, y] < 0:
                current_region += 1
                region[x, y] = current_region
                stack = [(x, y)]
                while stack:
                    x0, y0 = stack.pop()
                    this_color = img[x0, y0]
                    for i, j in get_neighbour(x0, y0):
                        if region[i, j] < 0 and img[i, j] == this_color:
                            region[i, j] = current_region
                            stack.append((i, j))
    return region

@dataclass
class RegionInfo:
    size: int
    color: int
    level: int
    top: int
    left: int
    bottom: int
    right: int
    # 不应该做数学、应该做几何。
    # def to_numpy(self):
    #     onehot_color = np.eye(10)[self.color]
    #     return np.array([self.size, *onehot_color, self.level,
    #                      self.top, self.left, self.bottom, self.right])

class Region:
    def __init__(self, img):
        self.img = img
        self.region = -np.ones(img.shape, int)
        self.region_info: List[RegionInfo] = []
        self.level = np.zeros(img.shape, int)
        self.current_region = -1
        boundary = []
        for x in range(img.shape[0]):
            boundary.append((x, 0))
            boundary.append((x, img.shape[1]-1))
        for y in range(img.shape[1]):
            boundary.append((0, y))
            boundary.append((img.shape[0]-1, y))
        bg_boundary = [(x, y) for x, y in boundary if img[x, y] == img.background_color]
        if not bg_boundary:
            print("No background color found in boundary")
            bg_boundary = boundary
        self.grow(bg_boundary, 0)
        # self.easy_region = easy_region(self.level)
    def get_neighbour(self, x, y):
        neighbour = []
        for i in range(x-1, x+2):
            if 0 <= i < self.img.shape[0]:
                for j in range(y-1, y+2):
                    if 0 <= j < self.img.shape[1]:
                        if (i, j) != (x, y):
                            neighbour.append((i, j))
        return neighbour
    def grow(self, boundary, level):
        next_boundary = []
        for x, y in boundary:
            if self.region[x, y] < 0:
                self.current_region += 1
                self.region[x, y] = self.current_region
                self.level[x, y] = level
                region_info = RegionInfo(1, self.img[x, y], level, x, y, x, y)
                stack = [(x, y)]
                while stack:
                    x0, y0 = stack.pop()
                    this_color = self.img[x0, y0]
                    for i, j in self.get_neighbour(x0, y0):
                        if self.region[i, j] < 0:
                            if self.img[i, j] == this_color:
                                self.region[i, j] = self.current_region
                                region_info.size += 1
                                region_info.top = min(region_info.top, i)
                                region_info.left = min(region_info.left, j)
                                region_info.bottom = max(region_info.bottom, i)
                                region_info.right = max(region_info.right, j)
                                self.level[i, j] = level
                                stack.append((i, j))
                            else:
                                next_boundary.append((i, j))
                self.region_info.append(region_info)
        if next_boundary:
            self.grow(next_boundary, level+1)
        return self.region


if __name__ == '__main__':
    from data import *
    from concept import *
    from reasoning import *
    data = get_data(True)['8e1813be']
    print(data.train[0].output)
    exemple = Region(data.train[0].output)
    print(exemple.region)
    print(exemple.region_info)
    print(exemple.level)
    print(exemple.easy_region)
