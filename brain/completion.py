from typing import Set, Optional
from dataclasses import dataclass
from brain.image import Image
from brain.rotate import *
from brain.region import region_from_color
from brain.move import do_move

@dataclass
class Completion:
    rotate_types: Set[RotateType]
    def __len__(self):
        return len(self.rotate_types)
    def __call__(self, img: Image) -> Image:
        unknown = region_from_color(img, 0)
        assert unknown.size == unknown.box_size
        imgs = [rt.inv()(img) for rt in self.rotate_types]
        def f(i, j):
            res = 0
            for img in imgs:
                c = img[i + unknown.top, j + unknown.left]
                if c != 0:
                    if res == 0:
                        res = c
                    elif res != c:
                        print("\033[93mConflicting colors\033[0m")
            if res == 0:
                print("\033[93mNo color found\033[0m")
            return res
        return Image.generate(f, unknown.heigth, unknown.width)


def find_completions(src: Image, dst: Image, k) -> Optional[Completion]:
    unknown = region_from_color(src, 0)
    if unknown.heigth != dst.height or unknown.width != dst.width:
        return None
    if unknown.size != unknown.box_size:
        return None
    if src.height % 2 == 1:
        center_xs = [src.height // 2]
    else:
        center_xs = [src.height // 2 - 1, src.height // 2]
    if src.width % 2 == 1:
        center_ys = [src.width // 2]
    else:
        center_ys = [src.width // 2 - 1, src.width // 2]
    if all([(center_x, center_y) in unknown.pixels
            for center_x in center_xs
            for center_y in center_ys]):
        return None
    complete_img = do_move(dst, src, unknown.top, unknown.left)
    rts = set()
    for rt in RotateType:
        if rt == RotateType.Nothing:
            continue
        if rt(complete_img) == complete_img:
            rts.add(rt)
    return Completion(rts)
