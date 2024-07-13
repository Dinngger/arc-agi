from typing import Optional, List, Set
from enum import Enum
from brain.image import Image

class RotateType(Enum):
    Nothing = 0
    UpDown = 1
    LeftRight = 2
    Center = 3      # same with rotate 180 degree
    Diagonal = 4
    Right = 5
    Left = 6
    AntiDiagonal = 7
    def __call__(self, img: Image) -> Image:
        h, w = transform(img.height, img.width, self)
        dx = -h-1 if h < 0 else 0
        dy = -w-1 if w < 0 else 0
        h, w = abs(h), abs(w)
        def f(i, j):
            return img[transform(i, j, self, dx=dx, dy=dy)]
        return Image.generate(f, h, w)

def is_rigid(rotate_type: RotateType) -> bool:
    return rotate_type in [RotateType.Nothing, RotateType.Left, RotateType.Right, RotateType.Center]

def transform(x, y, type, dx=0, dy=0):
    if type == RotateType.Nothing:
        return x + dx, y + dy
    elif type == RotateType.UpDown:
        return -x + dx, y + dy
    elif type == RotateType.LeftRight:
        return x + dx, -y + dy
    elif type == RotateType.Center:
        return -x + dx, -y + dy
    elif type == RotateType.Diagonal:
        return y + dx, x + dy
    elif type == RotateType.Right:
        return -y + dx, x + dy
    elif type == RotateType.Left:
        return y + dx, -x + dy
    elif type == RotateType.AntiDiagonal:
        return -y + dx, -x + dy


def is_rotate(a: Image, b: Image, rotate_type: RotateType, k='none') -> bool:
    h, w = transform(a.height, a.width, rotate_type)
    dx = -h-1 if h < 0 else 0
    dy = -w-1 if w < 0 else 0
    h, w = abs(h), abs(w)
    if h != b.height or w != b.width:
        return False
    for i in range(b.height):
        for j in range(b.width):
            if a[transform(i, j, rotate_type, dx=dx, dy=dy)] != b[i, j]:
                return False
    return True

def find_rotate(a: Image, b: Image, k='none') -> Set[RotateType]:
    return set([rt for rt in RotateType if is_rotate(a, b, rt, k)])
