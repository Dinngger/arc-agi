from dataclasses import dataclass
from typing import Optional
from brain.image import Image

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

def find_move(src: Image, dst: Image):
    possible_moves = []
    for dx in range(dst.height - src.height + 1):
        for dy in range(dst.width - src.width + 1):
            if is_move(src, dst, dx, dy):
                possible_moves.append((dx, dy))
    return possible_moves

def is_hconcat(src: Image, dst: Image):
    if dst.height != src.height or dst.width != src.width * 2:
        return False
    return is_move(src, dst, 0, 0) and is_move(src, dst, 0, src.width)

def do_hconcat(src: Image) -> Image:
    dst = Image.zeros(src.height, src.width * 2)
    dst = do_move(src, dst, 0, 0)
    dst = do_move(src, dst, 0, src.width)
    return dst

@dataclass
class Crop:
    dx: int
    dy: int
    height: int
    width: int
    def __call__(self, img: Image) -> Image:
        return Image.generate(lambda i, j: img[i + self.dx, j + self.dy], self.height, self.width)

@dataclass
class Expand:
    dx: int
    dy: int
    height: int
    width: int
    def __call__(self, img: Image) -> Image:
        res = Image.zeros(self.height, self.width)
        return do_move(img, res, self.dx, self.dy)

def is_crop(src: Image, dst: Image, crop: Crop) -> bool:
    if dst.height != crop.height or dst.width != crop.width:
        return False
    for i in range(crop.height):
        for j in range(crop.width):
            if src[i + crop.dx, j + crop.dy] != dst[i, j]:
                return False
    return True

def find_crop(src: Image, dst: Image, k='none') -> Optional[Crop]:
    if src.height < dst.height or src.width < dst.width:
        return None
    for dx in range(src.height - dst.height + 1):
        for dy in range(src.width - dst.width + 1):
            if is_crop(src, dst, Crop(dx, dy, dst.height, dst.width)):
                return Crop(dx, dy, dst.height, dst.width)
    return None
