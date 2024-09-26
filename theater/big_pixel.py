from dataclasses import dataclass
from typing import Optional, List
from theater.image import Color, Pixel, Image

@dataclass
class BigPixel:
    i: int
    j: int
    color: Color
    size: int
    @staticmethod
    def gen(pixel: Pixel) -> List['BigPixel']:
        res = []
        size = 2
        while True:
            for i in range(size):
                for j in range(size):
                    if not pixel.image.in_bound(pixel.i + i, pixel.j + j):
                        return res
                    if pixel.neighbor(i, j).color != pixel.color:
                        return res
            res.append(BigPixel(pixel.i, pixel.j, pixel.color, size))
            size += 1

@dataclass
class BigPixelImage:
    i: int
    j: int
    size: int
    image: Image
    @staticmethod
    def gen(pixels: List[BigPixel]) -> List['BigPixelImage']:
        if len(pixels) <= 1:
            return []
        first_pixel = pixels[0]
        s = first_pixel.size
        res = [first_pixel]
        left = []
        for pixel in pixels[1:]:
            if pixel.size == first_pixel.size and \
               (pixel.i - first_pixel.i) % s == 0 and \
               (pixel.j - first_pixel.j) % s == 0:
                res.append(pixel)
            else:
                left.append(pixel)
        bgs = []
        if len(res) > 1:
            min_i = min(p.i for p in res)
            max_i = max(p.i for p in res)
            min_j = min(p.j for p in res)
            max_j = max(p.j for p in res)
            height = (max_i - min_i) // s + 1
            width = (max_j - min_j) // s + 1
            color_img = [[None for j in range(width)] for i in range(height)]
            for p in res:
                color_img[(p.i - min_i) // s][(p.j - min_j) // s] = p.color
            not_full = False
            for i in range(height):
                for j in range(width):
                    if color_img[i][j] is None:
                        not_full = True
            if not not_full:
                bgs.append(BigPixelImage(first_pixel.i, first_pixel.j,
                                         first_pixel.size, Image.from_list(color_img)))
        return bgs + BigPixelImage.gen(left)
