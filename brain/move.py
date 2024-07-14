from dataclasses import dataclass
from typing import Optional, Set, Callable, List
from brain.image import Image
from brain.region import *
from brain.numbers import Counter
from brain.special import *

def do_move(src: Image, dst: Image, dx: int, dy: int) -> Image:
    def f(i, j):
        x, y = i - dx, j - dy
        if src.in_bound(x, y):
            return src[x, y]
        else:
            return dst[i, j]
    return Image.generate(f, dst.height, dst.width)

def is_move(src: Image, dst: Image, dx: int, dy: int) -> bool:
    for i in range(src.height):
        for j in range(src.width):
            if dst.in_bound(i + dx, j + dy):
                if src[i, j] != dst[i + dx, j + dy]:
                    return False
    return True

def is_hconcat(src: Image, dst: Image):
    if dst.height != src.height or dst.width != src.width * 2:
        return False
    return is_move(src, dst, 0, 0) and is_move(src, dst, 0, src.width)

def do_hconcat(src: Image) -> Image:
    dst = Image.zeros(src.height, src.width * 2)
    dst = do_move(src, dst, 0, 0)
    dst = do_move(src, dst, 0, src.width)
    return dst

def can_make_fraction(x, ref):
    return x == 0 or ref % x == 0

def make_fraction(x, ref):
    assert can_make_fraction(x, ref)
    return 0 if x == 0 else ref // x

@dataclass(frozen=True)
class Crop:
    fix_or_ratio: bool
    dx: int
    dy: int
    height: int
    width: int
    def __call__(self, img: Image) -> Image:
        if self.fix_or_ratio:
            return img[self.dx:self.dx+self.height, self.dy:self.dy+self.width]
        else:
            dx = make_fraction(self.dx, img.height)
            dy = make_fraction(self.dy, img.width)
            height = make_fraction(self.height, img.height)
            width = make_fraction(self.width, img.width)
            return img[dx:dx+height, dy:dy+width]

@dataclass(frozen=True)
class CropRegion:
    special_region: Callable[[List[Region]], Region]
    def __call__(self, img: Image) -> Image:
        regions = make_region(img)
        regions = [r for r in regions if r.color != 0]
        regions = combine_regions_in_box(regions)
        if len(regions) == 1:
            r = regions[0]
        else:
            r = self.special_region(regions)
        return img[r.top:r.bottom+1, r.left:r.right+1]

def is_fix_crop(src: Image, dst: Image, crop: Crop) -> bool:
    assert crop.fix_or_ratio
    if dst.height != crop.height or dst.width != crop.width:
        return False
    for i in range(crop.height):
        for j in range(crop.width):
            if src[i + crop.dx, j + crop.dy] != dst[i, j]:
                return False
    return True

def find_crop(src: Image, dst: Image, k='none') -> Set[Crop]:
    if src.height < dst.height or src.width < dst.width:
        return None
    hw_can_ratio = src.height % dst.height == 0 and src.width % dst.width == 0
    if hw_can_ratio:
        h = src.height // dst.height
        w = src.width // dst.width
    crops = set()
    for dx in range(src.height - dst.height + 1):
        for dy in range(src.width - dst.width + 1):
            if is_fix_crop(src, dst, Crop(True, dx, dy, dst.height, dst.width)):
                crops.add(Crop(True, dx, dy, dst.height, dst.width))
                if hw_can_ratio and can_make_fraction(dx, src.height) and can_make_fraction(dy, src.width):
                    crops.add(Crop(False, make_fraction(dx, src.height),
                                          make_fraction(dy, src.width), h, w))
    
    regions = make_region(src)
    regions = [r for r in regions if r.color != 0]
    regions = combine_regions_in_box(regions)
    if len(regions) == 0:
        print("no region found on", k)
        return None
    if len(regions) == 1:
        r = regions[0]
        if src[r.top:r.bottom+1, r.left:r.right+1] == dst:
            crops.add(CropRegion(None))
    else:
        size_counter = Counter([r.size for r in regions])
        if size_counter.count[size_counter.min] == 1:
            r = [r for r in regions if r.size == size_counter.min][0]
            if src[r.top:r.bottom+1, r.left:r.right+1] == dst:
                crops.add(CropRegion(MinSizeRegion()))
        if size_counter.count[size_counter.max] == 1:
            r = [r for r in regions if r.size == size_counter.max][0]
            if src[r.top:r.bottom+1, r.left:r.right+1] == dst:
                crops.add(CropRegion(MaxSizeRegion()))
        color_counter = Counter([r.color for r in regions])
        if color_counter.count[color_counter.least] == 1:
            r = [r for r in regions if r.color == color_counter.least][0]
            if src[r.top:r.bottom+1, r.left:r.right+1] == dst:
                crops.add(CropRegion(LeastColorRegion()))
    return crops
