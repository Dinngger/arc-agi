from dataclasses import dataclass
from typing import Set
from brain.image import Image
from brain.region import *

@dataclass(frozen=True)
class RegionMove:
    dx: int
    dy: int
    def __call__(self, img: Image) -> Image:
        regions = make_region(img)
        fg_regions = [r for r in regions if r.color != 0]
        res = Image.zeros(img.height, img.width)
        for r in fg_regions:
            r.paint_on(res, self.dx, self.dy)
        return res

def find_region_fix_move(src: Image, dst: Image, k) -> Set[RegionMove]:
    src_regions = make_region(src)
    dst_regions = make_region(dst)
    fg_src_regions = [r for r in src_regions if r.color != 0]
    fg_dst_regions = [r for r in dst_regions if r.color != 0]
    if len(fg_src_regions) != len(fg_dst_regions):
        return None
    possible_moves = None
    for dr in fg_dst_regions:
        possible_move = set()
        for sr in fg_src_regions:
            if sr.size != dr.size or sr.color != dr.color or \
               sr.heigth != dr.heigth or sr.width != dr.width:
                continue
            x, y = dr.top - sr.top, dr.left - sr.left
            for (dx, dy), (sx, sy) in zip(dr.pixels, sr.pixels):
                if dx != sx + x or dy != sy + y:
                    break
            else:
                possible_move.add(RegionMove(x, y))
        if not possible_move:
            return None
        if possible_moves is None:
            possible_moves = possible_move
        else:
            possible_moves = possible_moves.intersection(possible_move)
    return possible_moves
