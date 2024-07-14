from typing import Optional
from brain.image import Image
from brain.numbers import img_color_counter
from brain.region import *


def partial_change_from_color_region(src: Image, dst: Image, k) -> Optional[int]:
    if src.height != dst.height or src.width != dst.width:
        return None
    colors = img_color_counter(src).count.keys()
    diff_pixels = []
    for i in range(src.height):
        for j in range(src.width):
            if src[i, j] != dst[i, j]:
                diff_pixels.append((i, j))
    diff_region = region_from_pixels(diff_pixels)
    color_regions = [region_from_color(src, c) for c in colors]
    min_area = src.height * src.width
    min_region_color = None
    for cr in color_regions:
        if diff_region.in_region_box(cr):
            if cr.heigth * cr.width < min_area:
                min_area = cr.heigth * cr.width
                min_region_color = cr.color
    return min_region_color
