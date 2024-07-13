from dataclasses import dataclass
from brain.image import Image

def is_same_shape(a: Image, b: Image) -> bool:
    return a.height == b.height and a.width == b.width

@dataclass
class PureColor:
    def __call__(self, img: Image, color: int) -> Image:
        return img.self_generate(lambda i, x, y: color)

def is_pure_color(img: Image) -> bool:
    for i in range(img.height):
        for j in range(img.width):
            if img[i, j] != img[0, 0]:
                return False
    return True
