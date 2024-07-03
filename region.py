import numpy as np
from typing import Tuple, List
from dataclasses import dataclass
from data import Image

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
    pixels: List[Tuple[int, int]]
    @property
    def heigth(self):
        return self.bottom - self.top + 1
    @property
    def width(self):
        return self.right - self.left + 1
    def center(self, strict=True):
        if strict:
            assert self.heigth % 2 == 1 and self.width % 2 == 1
            return (self.top + self.bottom) // 2, (self.left + self.right) // 2
        else:
            return (self.top + self.bottom) / 2, (self.left + self.right) / 2
    def corners(self):
        return [((self.top, self.left), (-1, -1)),
                ((self.top, self.right), (-1, 1)),
                ((self.bottom, self.left), (1, -1)),
                ((self.bottom, self.right), (1, 1))]
    def copy(self):
        return RegionInfo(self.size, self.color, self.level,
                          self.top, self.left, self.bottom, self.right, 
                          self.pixels.copy())
    def in_region_box(self, ri):
        return (self.top >= ri.top and self.bottom <= ri.bottom and
                self.left >= ri.left and self.right <= ri.right)
    def box_overlap_with(self, ri):
        return (self.top <= ri.bottom and self.bottom >= ri.top and
                self.left <= ri.right and self.right >= ri.left)
    def full_of_box(self):
        return self.size == self.width * self.heigth
    def paint_on(self, target_img: Image, dx=0, dy=0, color=None):
        for x, y in self.pixels:
            target_img[x+dx, y+dy] = self.color if color is None else color
    def combine_with(self, other):
        assert self.color == other.color
        self.size += other.size
        self.level = min(self.level, other.level)
        self.top = min(self.top, other.top)
        self.left = min(self.left, other.left)
        self.bottom = max(self.bottom, other.bottom)
        self.right = max(self.right, other.right)
        self.pixels.extend(other.pixels)
    @staticmethod
    def box_region(top, left, bottom, right, color):
        ri = RegionInfo(0, color, -1, top, left, bottom, right, [])
        for x in range(top, bottom+1):
            for y in range(left, right+1):
                ri.size += 1
                ri.pixels.append((x, y))
        return ri
    @staticmethod
    def from_color(img: Image, color):
        region_info = RegionInfo(0, color, -1, -1, -1, -1, -1, [])
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                if img[x, y] == color:
                    region_info.size += 1
                    if region_info.top < 0:
                        region_info.top = x
                        region_info.left = y
                        region_info.bottom = x
                        region_info.right = y
                    else:
                        region_info.top = min(region_info.top, x)
                        region_info.left = min(region_info.left, y)
                        region_info.bottom = max(region_info.bottom, x)
                        region_info.right = max(region_info.right, y)
                    region_info.pixels.append((x, y))
        return region_info

def region_background_color(img: Image, ri: RegionInfo):
    color_count = {}
    for x, y in ri.pixels:
        c = img[x, y]
        if c not in color_count:
            color_count[c] = 0
        color_count[c] += 1
    most_color = max(color_count, key=color_count.get)
    return 0 if 0 in color_count else most_color   # maybe just try the two choices

def combine_regions_in_box(ris: List[RegionInfo]) -> List[RegionInfo]:
    n = len(ris)
    in_ris = [ri.copy() for ri in ris]
    res = []
    for i in range(n-1, -1, -1):
        for j in range(i-1, -1, -1):
            if in_ris[i].color == in_ris[j].color and in_ris[i].box_overlap_with(in_ris[j]):
                in_ris[j].combine_with(in_ris[i])
                break
        else:
            res.append(in_ris[i])
    return res

def easy_region(img: np.ndarray) -> Tuple[np.ndarray, List[RegionInfo]]:
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
                region_info = RegionInfo(1, -1, img[x, y], x, y, x, y, [(x, y)])
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
    def __init__(self, img: Image, strict_neighbour=False):
        self.img: Image = img
        self.strict_neighbour = strict_neighbour
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
            for hri in hr_info:
                hri.color = region_background_color(img, hri)
            self.hierarchical_regions.append(hr)
            self.hierarchical_region_infos.append(hr_info)
    def get_neighbour(self, x, y):
        if self.strict_neighbour:
            neighbour = [(i, j) for i, j in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                         if self.img.in_bound(i, j) and (i, j) != (x, y)]
        else:
            neighbour = [(i, j) for i in range(x-1, x+2) for j in range(y-1, y+2)
                         if self.img.in_bound(i, j) and (i, j) != (x, y)]
        return neighbour
    def grow(self, boundary, level):
        next_boundary = []
        for x, y in boundary:
            if self.region[x, y] < 0:
                self.current_region += 1
                self.region[x, y] = self.current_region
                self.level[x, y] = level
                region_info = RegionInfo(1, self.img[x, y], level, x, y, x, y, [(x, y)])
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
                self.region_info.append(region_info)
        if next_boundary:
            self.grow(next_boundary, level+1)
        return self.region


if __name__ == '__main__':
    from data import *
    from concept import *
    from reasoning import *
    data = get_data(True)['0b148d64']
    exemple = Region(data.train[1].input)
    print(exemple.region)
    print(exemple.region_info)
    print('Combined regions:')
    print(combine_regions_in_box(exemple.region_info))
    print('Level:')
    print(exemple.level)
    for l, hr in enumerate(exemple.hierarchical_regions):
        print(f"Level {l}:")
        print(hr)
    print(exemple.hierarchical_region_infos)
