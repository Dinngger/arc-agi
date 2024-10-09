from math import ceil
from typing import List, Tuple, Optional
from datatypes import *


@dataclass
class DrawRect:
    pos: Position
    shape: Shape
    color: Color
    def is_row_line(self) -> bool:
        return self.shape.h == 1
    def is_col_line(self) -> bool:
        return self.shape.w == 1
    def is_square(self) -> bool:
        return self.shape.h == self.shape.w
    @staticmethod
    def draw_rect(x: Image, i, j, h, w, color):
        img = x.copy()
        for x in range(i, i+h):
            for y in range(j, j+w):
                img[x, y] = color
        return img
    @staticmethod
    def remove_rect(x: Image, rect: 'DrawRect'):
        img = x.copy()
        for x in range(rect.pos.i, rect.pos.i+rect.shape.h):
            for y in range(rect.pos.j, rect.pos.j+rect.shape.w):
                if img[x, y] == rect.color:
                    img[x, y] = 10
        return img
    @staticmethod
    def find_rect(img: Image) -> Optional['DrawRect']:
        # return biggest rects
        max_area = 0
        max_rect = None
        for i in range(img.height):
            for j in range(img.width):
                if img[i, j] == 10:
                    continue
                for h in range(i, img.height):
                    if img[h, j] == 10:
                        break
                    height = h - i + 1
                    color_count = {}
                    for w in range(j, img.width):
                        pure = True
                        for k in range(i, h + 1):
                            c = img[k, w]
                            if img[k, w] == 10:
                                pure = False
                                break
                            if c not in color_count:
                                color_count[c] = 0
                            color_count[c] += 1
                        if not pure:
                            break
                        current_area = height * (w - j + 1)
                        if current_area > max_area:
                            max_area = current_area
                            most_color = max(color_count, key=color_count.get)
                            max_rect = DrawRect(Position(i, j), Shape(height, w - j + 1), most_color)
        return max_rect


class PureImage:
    @staticmethod
    def gen(h, w, c):
        img = [[c for j in range(w)] for i in range(h)]
        return Image(img)
    @staticmethod
    def find_pure_image(img: Image) -> Optional['DrawRect']:
        """ is the image have background? """
        color_count = {}
        for row in img.list:
            for x in row:
                if x not in color_count:
                    color_count[x] = 0
                color_count[x] += 1
        most_color = max(color_count, key=color_count.get)
        background_color = 0 if 0 in color_count else most_color   # maybe just try the two choices
        return DrawRect(Position(0, 0), Shape(img.height, img.width), background_color)


class ImageCopy:
    @staticmethod
    def copy(src: Image, dst: Image, i, j):
        dst = dst.copy()
        for x in range(i, i+src.height):
            for y in range(j, j+src.width):
                c = src[x-i, y-j]
                if c != 10:
                    dst[x, y] = c
        return dst
