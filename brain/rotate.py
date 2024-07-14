from typing import Optional, List, Set
from enum import Enum
from brain.image import Image

inv_rotate = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 5, 7: 7}

class RotateType(Enum):
    Nothing = 0
    UpDown = 1
    LeftRight = 2
    Center = 3      # same with rotate 180 degree
    Diagonal = 4
    Right = 5
    Left = 6
    AntiDiagonal = 7
    def __repr__(self):
        return self.name
    def __call__(self, img: Image) -> Image:
        h, w = transform(img.height, img.width, self)
        dx = -h-1 if h < 0 else 0
        dy = -w-1 if w < 0 else 0
        h, w = abs(h), abs(w)
        def f(i, j):
            return img[inv_transform(i, j, self, dx=dx, dy=dy)]
        return Image.generate(f, h, w)
    def inv(self):
        return RotateType(inv_rotate[self.value])

def is_rigid(rotate_type: RotateType) -> bool:
    return rotate_type in [RotateType.Nothing, RotateType.Left, RotateType.Right, RotateType.Center]


def rotate(x, y, type):
    if type == RotateType.Nothing:
        return x, y
    elif type == RotateType.UpDown:
        return -x, y
    elif type == RotateType.LeftRight:
        return x, -y
    elif type == RotateType.Center:
        return -x, -y
    elif type == RotateType.Diagonal:
        return y, x
    elif type == RotateType.Right:
        return -y, x
    elif type == RotateType.Left:
        return y, -x
    elif type == RotateType.AntiDiagonal:
        return -y, -x

def transform(x, y, type, dx=0, dy=0):
    x, y = rotate(x, y, type)
    return x + dx, y + dy

def inv_transform(x, y, type: RotateType, dx=0, dy=0):
    return rotate(x - dx, y - dy, type.inv())

def is_rotate(a: Image, b: Image, rotate_type: RotateType, k='none') -> bool:
    h, w = transform(a.height, a.width, rotate_type)
    dx = -h-1 if h < 0 else 0
    dy = -w-1 if w < 0 else 0
    h, w = abs(h), abs(w)
    if h != b.height or w != b.width:
        return False
    for i in range(b.height):
        for j in range(b.width):
            if a[inv_transform(i, j, rotate_type, dx=dx, dy=dy)] != b[i, j]:
                return False
    return True

def find_rotate(a: Image, b: Image, k='none') -> Set[RotateType]:
    return set([rt for rt in RotateType if is_rotate(a, b, rt, k)])
