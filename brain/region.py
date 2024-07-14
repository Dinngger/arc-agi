from typing import Tuple, List
from dataclasses import dataclass
from brain.image import Image


@dataclass
class Region:
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
    @property
    def box_size(self):
        return self.heigth * self.width
    def copy(self):
        return Region(self.size, self.color, self.level,
                      self.top, self.left, self.bottom, self.right, 
                      self.pixels.copy())
    def in_region_box(self, ri):
        return (self.top >= ri.top and self.bottom <= ri.bottom and
                self.left >= ri.left and self.right <= ri.right)
    def box_overlap_with(self, ri):
        return (self.top <= ri.bottom and self.bottom >= ri.top and
                self.left <= ri.right and self.right >= ri.left)
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

def get_neighbour(img: Image, x, y, strict=False):
    if strict:
        neighbour = [(i, j) for i, j in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                        if img.in_bound(i, j) and (i, j) != (x, y)]
    else:
        neighbour = [(i, j) for i in range(x-1, x+2) for j in range(y-1, y+2)
                        if img.in_bound(i, j) and (i, j) != (x, y)]
    return neighbour

def make_region(img: Image) -> List[Region]:
    region_img = img.self_generate(lambda i, x, y: -1)
    regions: List[Region] = []
    boundary = []
    for x in range(img.height):
        boundary.append((x, 0))
        boundary.append((x, img.width-1))
    for y in range(img.width):
        boundary.append((0, y))
        boundary.append((img.height-1, y))
    bg_boundary = [(x, y) for x, y in boundary if img[x, y] == 0]
    if not bg_boundary:
        # print("No background color 0 found in boundary")
        bg_boundary = boundary

    now_boundary = bg_boundary
    now_level = 0
    now_region = -1
    while now_boundary:
        next_boundary = []
        for x, y in now_boundary:
            if region_img[x, y] < 0:
                now_region += 1
                region_img[x, y] = now_region
                region = Region(1, img[x, y], now_level, x, y, x, y, [(x, y)])
                stack = [(x, y)]
                while stack:
                    x0, y0 = stack.pop()
                    this_color = img[x0, y0]
                    for i, j in get_neighbour(img, x0, y0):
                        if region_img[i, j] < 0:
                            if img[i, j] == this_color:
                                region_img[i, j] = now_region
                                region.size += 1
                                region.top = min(region.top, i)
                                region.left = min(region.left, j)
                                region.bottom = max(region.bottom, i)
                                region.right = max(region.right, j)
                                region.pixels.append((i, j))
                                stack.append((i, j))
                            else:
                                next_boundary.append((i, j))
                regions.append(region)
        now_boundary = next_boundary
        now_level += 1
    return regions

def region_from_pixels(pixels: List[Tuple[int, int]]) -> Region:
    region = Region(len(pixels), -1, -1, -1, -1, -1, -1, pixels)
    for x, y in pixels:
        if region.top < 0:
            region.top = x
            region.left = y
            region.bottom = x
            region.right = y
        else:
            region.top = min(region.top, x)
            region.left = min(region.left, y)
            region.bottom = max(region.bottom, x)
            region.right = max(region.right, y)
    return region

def region_from_color(img: Image, color):
    pixels = []
    for x in range(img.height):
        for y in range(img.width):
            if img[x, y] == color:
                pixels.append((x, y))
    region = region_from_pixels(pixels)
    region.color = color
    return region

def combine_regions_in_box(ris: List[Region]) -> List[Region]:
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
