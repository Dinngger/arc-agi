from math import gcd
from functools import reduce
from data import *
from region import Region, RegionInfo

def find_big_pixel(ri: RegionInfo):
    bounderies = set()
    for i in range(ri.top, ri.bottom+1):
        for j in range(ri.left, ri.right+1):
            if ((i, j) in ri.pixels) ^ ((i, j+1) in ri.pixels):
                bounderies.add(j - ri.left + 1)
            if ((i, j) in ri.pixels) ^ ((i+1, j) in ri.pixels):
                bounderies.add(i - ri.top + 1)
    pixel_size = reduce(gcd, bounderies)
    if pixel_size == 1:
        return 1, None
    pixels = set()
    for i, j in ri.pixels:
        pixels.add(((i - ri.top) // pixel_size, (j - ri.left) // pixel_size))
    return pixel_size, pixels

def solve_c444b776(img: Image):
    remove_yellow = img.self_generate(lambda img, x, y: 0 if img[x, y] != 4 else 4)
    region = Region(remove_yellow)
    for ri in region.region_info:
        if ri.color == 4:
            continue
        for i, j in ri.pixels:
            if img[i, j] != 0:
                x, y = ri.top, ri.left
                break
    for ri in region.region_info:
        if ri.color == 4:
            continue
        for i in range(ri.bottom+1-ri.top):
            for j in range(ri.right+1-ri.left):
                remove_yellow[ri.top+i, ri.left+j] = img[x+i, y+j]
    return remove_yellow

def solve_6ecd11f4(img: Image):
    region = Region(img)
    for ri in region.region_info:
        if ri.size > 4 and ri.color != 0:
            pixel_size, pixels = find_big_pixel(ri)
            assert pixel_size > 1
    colorful_region = [ri.pixels for ri in region.region_info if ri.color != 0 and ri.size <= 4]
    xs = [p[0] for ps in colorful_region for p in ps]
    ys = [p[1] for ps in colorful_region for p in ps]
    top, left, bottom, right = min(xs), min(ys), max(xs), max(ys)
    new_img = img.subimage(top, left, bottom, right)
    return new_img.generate(lambda x, y: new_img[x, y] if (x, y) in pixels else 0, new_img.shape)

def solve_c909285e(img: Image):
    region = Region(img)
    color_region_count = {}
    for ri in region.region_info:
        if ri.color not in color_region_count:
            color_region_count[ri.color] = 1
        else:
            color_region_count[ri.color] += 1
    for color, count in color_region_count.items():
        if count == 1:
            special_color = color
            break
    for ri in region.region_info:
        if ri.color == special_color:
            return img.subimage(ri.top, ri.left, ri.bottom, ri.right)

def solve_88a10436(img: Image):
    decolor = img.generate(lambda x, y: img[x, y] if img[x, y] in [0, 5] else 1, img.shape)
    region = Region(decolor)
    res = img.copy()
    for ri in region.region_info:
        if ri.color == 5:
            tx, ty = ri.top, ri.left
            break
    for ri in region.region_info:
        if ri.color == 1:
            for i in range(ri.top, ri.bottom+1):
                for j in range(ri.left, ri.right+1):
                    res[tx+i-ri.top-1, ty+j-ri.left-1] = img[i, j]
    return res
