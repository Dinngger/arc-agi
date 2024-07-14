from dataclasses import dataclass
from typing import Optional, Set
from brain.image import Image

class NoisedBlock:
    def __init__(self, color=None, cnt=0):
        self.color: Set[int] = set() if color is None else color
        self.cnt: int = cnt

def is_same_color(img: Image, color: int) -> NoisedBlock:
    noise = NoisedBlock()
    for i in range(img.height):
        for j in range(img.width):
            if img[i, j] != color:
                noise.color.add(img[i, j])
                noise.cnt += 1
    return noise

def is_scale_up(a: Image, b: Image, scale: int) -> bool:
    if a.height * scale != b.height or a.width * scale != b.width:
        return False
    for i in range(b.height):
        for j in range(b.width):
            if a[i // scale, j // scale] != b[i, j]:
                return False
    return True

def is_scale_down(a: Image, b: Image, scale: int) -> bool:
    if b.height * scale != a.height or b.width * scale != a.width:
        return False
    for i in range(a.height):
        for j in range(a.width):
            if b[i // scale, j // scale] != a[i, j]:
                return False
    return True

def denoise(img: Image, noise_color: int) -> int:
    cs = [img[i, j] for i in range(img.height)
                    for j in range(img.width)
                    if img[i, j] != noise_color]
    cs = set(cs)
    assert len(cs) == 1
    return cs.pop()

@dataclass
class NoisedScaleDown:
    scale: int
    noise_color: int
    def __call__(self, img: Image) -> Image:
        s = self.scale
        h, w = img.height // s, img.width // s
        def f(i, j):
            sub_img = img[i * s:(i+1) * s, j * s:(j+1) * s]
            return denoise(sub_img, self.noise_color)
        return Image.generate(f, h, w)

def find_noised_scale_down(a: Image, b: Image, s: int, k='none') -> Optional[NoisedScaleDown]:
    if b.height * s != a.height or b.width * s != a.width:
        return None
    nc = None
    for i in range(b.height):
        for j in range(b.width):
            nb = is_same_color(a[i*s:(i+1)*s, j*s:(j+1)*s], b[i, j])
            if len(nb.color) > 1 or nb.cnt > s*s/2:
                return None
            if len(nb.color) == 0:
                continue
            if nc is None:
                nc = nb.color.pop()
            elif nb.color.pop() != nc:
                return None
    return NoisedScaleDown(s, nc)

@dataclass
class ScaleUp:
    def __call__(self, img: Image, scale: int) -> Image:
        h, w = img.height * scale, img.width * scale
        def f(i, j):
            return img[i // scale, j // scale]
        return Image.generate(f, h, w)

def do_scale_down(img: Image, scale: int) -> Image:
    h, w = img.height // scale, img.width // scale
    def f(i, j):
        return img[i * scale, j * scale]
    return Image.generate(f, h, w)
