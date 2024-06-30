import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

DEBUG = False


@dataclass
class RegionInfo:
    size: int
    color: int
    level: int
    top: int
    left: int
    bottom: int
    right: int
    left_right_symmetry: bool
    pixels: List[Tuple[int, int]]
    @property
    def heigth(self):
        return self.bottom - self.top + 1
    @property
    def width(self):
        return self.right - self.left + 1
    def center(self):
        assert self.heigth % 2 == 1 and self.width % 2 == 1
        return (self.top + self.bottom) // 2, (self.left + self.right) // 2


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
    region_infos = []
    current_region = -1
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if region[x, y] < 0:
                current_region += 1
                region[x, y] = current_region
                region_info = RegionInfo(1, -1, img[x, y], x, y, x, y, False, [(x, y)])
                stack = [(x, y)]
                while stack:
                    x0, y0 = stack.pop()
                    this_color = img[x0, y0]
                    for i, j in get_neighbour(x0, y0):
                        if region[i, j] < 0 and img[i, j] == this_color:
                            region[i, j] = current_region
                            region_info.size += 1
                            region_info.top = min(region_info.top, i)
                            region_info.left = min(region_info.left, j)
                            region_info.bottom = max(region_info.bottom, i)
                            region_info.right = max(region_info.right, j)
                            region_info.pixels.append((i, j))
                            stack.append((i, j))
                if region_info.level > 0:
                    region_info.left_right_symmetry = left_right_symmetry(region_info)
                    region_infos.append(region_info)
    return region, region_infos

def left_right_symmetry(ri: RegionInfo):
    if (ri.right - ri.left + 1) % 2 == 1:
        return False
    if len(ri.pixels) % 2 == 1:
        return False
    middle_y = (ri.right + ri.left) / 2
    symmetry_y = lambda y: middle_y - (y - middle_y)
    temp_set = set()
    for x, y in ri.pixels:
        symmetry_xy = (x, symmetry_y(y))
        if symmetry_xy in temp_set:
            temp_set.remove(symmetry_xy)
        else:
            temp_set.add((x, y))
    return len(temp_set) == 0

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
            if DEBUG: print("No background color found in boundary")
            bg_boundary = boundary
        self.grow(bg_boundary, 0)
        self.num = self.current_region + 1
        self.hierarchical_regions = [None]
        self.hierarchical_region_infos: List[List[RegionInfo]] = [None]
        for level in range(1, self.level.max() + 1):
            level_img = self.level.copy()
            level_img[level_img > level] = level
            level_img[level_img < level] = 0
            hr, hr_info = easy_region(level_img)
            self.hierarchical_regions.append(hr)
            self.hierarchical_region_infos.append(hr_info)
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
                region_info = RegionInfo(1, self.img[x, y], level, x, y, x, y, False, [(x, y)])
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
                                region_info.pixels.append((i, j))
                                self.level[i, j] = level
                                stack.append((i, j))
                            else:
                                next_boundary.append((i, j))
                region_info.left_right_symmetry = left_right_symmetry(region_info)
                self.region_info.append(region_info)
        if next_boundary:
            self.grow(next_boundary, level+1)
        return self.region


if __name__ == '__main__':
    from data import *
    from concept import *
    from reasoning import *
    data = get_data(True)['264363fd']
    print(data.train[2].input)
    exemple = Region(data.train[2].input)
    print(exemple.region)
    print(exemple.region_info)
    print('Level:')
    print(exemple.level)
    for l, hr in enumerate(exemple.hierarchical_regions):
        print(f"Level {l}:")
        print(hr)
    print(exemple.hierarchical_region_infos)
