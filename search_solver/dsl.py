from math import ceil
from typing import List, Tuple, Optional
from collections import defaultdict
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


def merge_polymers(polymers: List[Polymer]) -> Polymer:
    return Polymer([p_p for p in polymers for p_p in p.pixels])

def aggregation(img: Image, polymers: List[Polymer], relation: FCanCat) -> List[Polymer]:
    n = len(polymers)
    domains = -np.ones(n, dtype=int)
    current_domain = -1
    for i in range(n):
        if domains[i] == -1:
            current_domain += 1
            domains[i] = current_domain
            stack = [i]
            while stack:
                j = stack.pop()
                # Too Slow!
                for k in range(j+1, n):
                    if domains[k] == -1 and relation.call(img, polymers[j], polymers[k]):
                        domains[k] = current_domain
                        stack.append(k)
    results = []
    for d in range(current_domain + 1):
        ps = [polymers[i] for i in range(n) if domains[i] == d]
        results.append(merge_polymers(ps))
    return results

def aggregation2d(img: Image, relation: FNeighbors) -> List[Polymer]:
    h, w = img.shape
    domains = -np.ones((h, w), dtype=int)
    current_domain = -1
    for i in range(h):
        for j in range(w):
            if domains[i, j] == -1:
                current_domain += 1
                domains[i, j] = current_domain
                stack = [Position(i, j)]
                while stack:
                    p = stack.pop()
                    for pp in relation.call(img, p):
                        ii, jj = pp.i, pp.j
                        if domains[ii, jj] == -1:
                            domains[ii, jj] = current_domain
                            stack.append(pp)
    polymers = []
    for d in range(current_domain + 1):
        pixels = []
        for i in range(h):
            for j in range(w):
                if domains[i, j] == d:
                    pixels.append(Position(i, j))
        polymers.append(Polymer(pixels))
    return polymers

def split_polymers(img: Image, polymers: List[Polymer]) -> List[Polymer]:
    # only keep the spilted polymers that with different shape of the image.
    result = []
    for p in polymers:
        tmp_img = Image([[0 for _ in range(img.width)] for _ in range(img.height)])
        for p_p in p.pixels:
            tmp_img[p_p] = 1
        new_polymers = aggregation2d(tmp_img, FNeighbors())
        for new_p in new_polymers:
            if tmp_img[new_p.pixels[0]] == 1:
                continue
            if new_p.shape == img.shape:
                continue
            result.append(new_p)
    return result

def aggregate_to_image(img: Image, polymers: List[Polymer]) -> List[Image]:
    # 由于Image是特殊概念，因此定义该函数
    # 一个polymer对应一个像素
    rows = defaultdict(list)
    cols = defaultdict(list)
    for i, p in enumerate(polymers):
        rows[(p.pos.i, p.shape.h)].append(i)
        cols[(p.pos.j, p.shape.w)].append(i)
    max_row = max(len(v) for v in rows.values())
    max_col = max(len(v) for v in cols.values())
    rows = [row for row in rows.values() if len(row) == max_row]
    cols = [col for col in cols.values() if len(col) == max_col]
    if len(rows) != max_col or len(cols) != max_row:
        return []
    print(f"found a image of ({max_col}, {max_row}) consisted by polymers")
    rows = [sorted(row, key=lambda i: polymers[i].pos.j) for row in rows]
    rows = sorted(rows, key=lambda row: polymers[row[0]].pos.i)
    def color_func(i: int):
        colors = Counter([img[p] for p in polymers[i].pixels])
        c, num = colors.most_common(1)[0]
        return c
    img = [[color_func(i) for i in row] for row in rows]
    return [Image(img)]
