import os
import json
from typing import List, Dict, Callable
from brain.image import Image
from brain.rotate import *
from brain.big_pixel import *
from brain.move import *
from brain.color import *
from brain.paint import *
from brain.numbers import *
from brain.diff import *
from brain.region_move import *
from brain.completion import *

class Sample:
    def __init__(self, s, o=None):
        if isinstance(s, dict):
            self.input = Image(s['input'])
            self.output = Image(s['output'])
        else:
            self.input = s
            self.output = o

class Data:
    def __init__(self, data):
        self.data = data
        self.train = [Sample(s) for s in data['train']]
        self.test = [Sample(s) for s in data['test']]

def check_all(f, ss):
    for s in ss:
        if not f(s.input, s.output):
            return False
    return True

def check_all_same(f, ss: List[Sample], k='none'):
    p = None
    for s in ss:
        p0 = f(s.input, s.output, k=k)
        if p0 is None:
            return None
        if p is None:
            p = p0
        elif p != p0:
            return None
    return p

def find_common(f, ss: List[Sample], k='none'):
    p = None
    for s in ss:
        p0: Set = f(s.input, s.output, k=k)
        if not p0:
            return None
        if p is None:
            p = p0
        else:
            p.intersection_update(p0)
    if not p:
        return None
    if len(p) > 1:
        print(f'{k} has Too many common values: {p}')
    return list(p)[0]

@dataclass
class Concat:
    h_or_v: bool
    a: RotateType
    b: RotateType
    def __call__(self, img: Image) -> Image:
        img_a = self.a(img)
        img_b = self.b(img)
        if self.h_or_v:
            dst = Image.zeros(img.height, img.width * 2)
            dst = do_move(img_a, dst, 0, 0)
            dst = do_move(img_b, dst, 0, img.width)
        else:
            dst = Image.zeros(img.height * 2, img.width)
            dst = do_move(img_a, dst, 0, 0)
            dst = do_move(img_b, dst, img.height, 0)
        return dst

def find_concat(i: Image, o: Image, k='none'):
    if o.height == i.height and o.width == i.width * 2:
        h_or_v = True
        a_img = o[:, :o.width//2]
        b_img = o[:, o.width//2:]
    elif o.height == i.height * 2 and o.width == i.width:
        h_or_v = False
        a_img = o[:o.height//2, :]
        b_img = o[o.height//2:, :]
    else:
        return None
    a = find_rotate(i, a_img, k)
    b = find_rotate(i, b_img, k)
    if (not a) or (not b):
        return None
    return Concat(h_or_v, a, b)

def find_common_concat(f, ss: List[Sample], k='none'):
    p = None
    for s in ss:
        p0 = f(s.input, s.output, k=k)
        if p0 is None:
            return None
        if p is None:
            p = p0
        else:
            if p.h_or_v != p0.h_or_v:
                return None
            p.a.intersection_update(p0.a)
            p.b.intersection_update(p0.b)
    if p is None:
        return None
    if len(p.a) == 1 and len(p.b) == 1:
        return Concat(p.h_or_v, list(p.a)[0], list(p.b)[0])
    if len(p.a) == 0 or len(p.b) == 0:
        return None
    assert False, f'Too many common values: {p}'

@dataclass
class Composite:
    a: Callable[[Image], int]
    b: Callable[[Image, int], Image]
    def __call__(self, img: Image) -> Image:
        return self.b(img, self.a(img))

@dataclass
class ConstInt:
    value: int
    def __call__(self, img: Image) -> int:
        return self.value

def find_common_pure_color(ss: List[Sample], k='none'):
    if not check_all(is_same_shape, ss):
        return None
    for s in ss:
        if not is_pure_color(s.output):
            return None
        counter = img_color_counter(s.input)
        if counter.most != s.output[0, 0]:
            return None
    return Composite(MostColor(), PureColor())

def find_completion(ss: List[Sample], k='none'):
    p = None
    for s in ss:
        p0 = find_completions(s.input, s.output, k)
        if not p0:
            return None
        if p is None:
            p = p0
        else:
            p.rotate_types.intersection_update(p0.rotate_types)
    if not p:
        return None
    return p

def find_scale_up(ss: List[Sample], k='none'):
    scales = []
    for sample in ss:
        for scale in [2, 3, 4, 5]:
            if is_scale_up(sample.input, sample.output, scale):
                scales.append(scale)
                break
        else:
            return None
    if all(s == scales[0] for s in scales):
        return Composite(ConstInt(scales[0]), ScaleUp())
    color_counts = [ColorCount()(s.input) for s in ss]
    if all(s == c for s, c in zip(scales, color_counts)):
        return Composite(ColorCount(), ScaleUp())
    print(f'Cannot find scale up pattern: {scales} for {k}')
    return None

def solver(data: Data, k='none'):
    p = find_common(find_rotate, data.train)
    if p is not None:
        print(f'Found pattern for {p.name}')
        return p
    p = find_scale_up(data.train, k)
    if p is not None:
        print(f'Found pattern for scale up {p}')
        return p
    for s in [2, 3]:
        p = check_all_same(lambda i, o, k: find_noised_scale_down(i, o, s, k), data.train, k)
        if p is not None:
            print(f'Found pattern for noised scale down {p}')
            return p
    p = check_all_same(find_color_transform, data.train)
    if p is not None:
        print(f'Found pattern for color transform {p}')
        return lambda img: do_color_transform(img, p)
    p = find_common(find_crop, data.train, k)
    if p is not None:
        print(f'Found pattern for crop {p}')
        return p
    p = find_common_concat(find_concat, data.train, k=k)
    if p is not None:
        print(f'Found pattern for concat {p}')
        return p
    p = find_common_pure_color(data.train, k=k)
    if p is not None:
        print(f'Found pattern for pure color {p}')
        return p
    p = find_common(find_region_fix_move, data.train, k=k)
    if p is not None:
        print(f'Found pattern for region fix move {p}')
        return p
    p = find_completion(data.train, k=k)
    if p is not None:
        print(f'{k}: Found pattern for completion {p}')
        return p
    p = check_all_same(partial_change_from_color_region, data.train, k=k)
    if p is not None:
        croped_ss = []
        for s in data.train:
            r = region_from_color(s.input, p)
            i = s.input[r.top:r.bottom+1, r.left:r.right+1]
            o = s.output[r.top:r.bottom+1, r.left:r.right+1]
            croped_ss.append(Sample(i, o))
        pp = check_all_same(find_color_transform, croped_ss)
        if pp is not None:
            print(f'Found pattern for partial color transform {pp}')
            def f(img):
                r = region_from_color(img, p)
                sub_img = img[r.top:r.bottom+1, r.left:r.right+1]
                diff = do_color_transform(sub_img, pp)
                return do_move(diff, img, r.top, r.left)
            return f
    return None

def load_data(path) -> Dict[str, Data]:
    data: Dict[str, Data] = {}
    for fn in os.listdir(path):
        with open(f'{path}/{fn}') as f:
            data[fn.rstrip('.json')] = Data(json.load(f))
    return data
