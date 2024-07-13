from typing import Dict, Optional
from brain.image import Image

def do_color_transform(img: Image, table: Dict[int, int]) -> Image:
    def f(i, j):
        if img[i, j] in table:
            return table[img[i, j]]
        else:
            return img[i, j]
    return Image.generate(f, img.height, img.width)

def find_color_transform(a: Image, b: Image, k='none') -> Optional[Dict[int, int]]:
    if a.height != b.height or a.width != b.width:
        return None
    stable_set = set()
    table = {}
    for i in range(a.height):
        for j in range(a.width):
            if a[i, j] == b[i, j]:
                stable_set.add(a[i, j])
                continue
            if a[i, j] in stable_set:
                return None
            if a[i, j] not in table:
                table[a[i, j]] = b[i, j]
            else:
                if b[i, j] != table[a[i, j]]:
                    return None
    return table
