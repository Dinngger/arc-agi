import numpy as np
from typing import List
from region import Region, RegionInfo, combine_regions_in_box
from data import Image, Sample, Data
from registration import find_position_map
from celer import Lasso


def region_bool_prediction(samples: List[Sample]):
    # predict weather a region will be left,
    # and weather a region will be moved.
    ys = []
    xs = []
    for s in samples:
        region = Region(s.input)
        offset = find_position_map(s)
        if offset is None:
            return
        
        # predict targets:
        removed = [len(x) == 0 for x in offset]
        if s.input.shape == s.output.shape:
            keep_still = [len(x) == 1 and x[0] == (0, 0) for x in offset]
        else:
            keep_still = [False] * region.num

        # source:
        is_background = np.array([ri.color == s.input.background_color for ri in region.region_info])
        size = [ri.size for ri in region.region_info]
        size_without_bg = [0 if bg else s for bg, s in zip(is_background, size)]
        max_size = max(size_without_bg)
        min_size = min([s for s in size_without_bg if s > 0])
        is_max_size = np.array([s == max_size for s in size])
        is_min_size = np.array([s == min_size for s in size])
        left_right_symmetry = np.array([ri.left_right_symmetry for ri in region.region_info])
        color = np.array([ri.color for ri in region.region_info])
        color = np.eye(10)[color]
        ys.append(np.stack([removed, keep_still], axis=-1))
        xs.append(np.hstack([np.stack([is_background, is_max_size, is_min_size, left_right_symmetry], axis=-1), color]))
    xs = np.vstack(xs)
    ys = np.vstack(ys)
    estimator = Lasso(alpha=0.01)
    estimator.fit(xs, ys)
    pred = np.zeros_like(ys)
    for i in range(ys.shape[1]):
        for j in range(xs.shape[1]):
            if estimator.coef_[i, j] > 0.1:
                pred[:, i] = np.logical_or(pred[:, i], xs[:, j])
            elif estimator.coef_[i, j] < -0.1:
                pred[:, i] = np.logical_or(pred[:, i], np.logical_not(xs[:, j]))
    error = np.logical_xor(pred, ys).sum()
    nonzero = (np.abs(estimator.coef_) > 1e-6).sum()
    if error > 0:
        print(np.hstack([xs, ys]))
        estimator.fit(xs, ys)
        print(estimator.coef_)
        print(f'Error: {error}, nonzero: {nonzero}')
    else:
        print('Success with nonzero:', nonzero)

def paint_region(img: Image, region: RegionInfo, dx, dy):
    for x0, y0 in region.pixels:
        x = x0 + dx - region.top
        y = y0 + dy - region.left
        if not img.in_bound(x, y):
            return False
        if img[x, y] != img.background_color:
            return False
        img[x, y] = region.color
    return True

def solve_681b3aeb(img: Image):
    region_info = Region(img).region_info
    region_info = [ri for ri in region_info if ri.color != img.background_color]
    # 使用深度优先搜索找到不发生碰撞的解
    region_pos = [(0, 0)]
    while region_pos:
        x, y = region_pos.pop()
        res = Image.zeros((3, 3))
        for p, ri in zip(region_pos, region_info):
            assert paint_region(res, ri, p[0], p[1])
        if paint_region(res, region_info[len(region_pos)], x, y):
            region_pos.append((x, y))
            if len(region_pos) == len(region_info):
                return res
            region_pos.append((0, 0))
        else:
            while True:
                if y < 2:
                    region_pos.append((x, y + 1))
                    break
                elif x < 2:
                    region_pos.append((x + 1, 0))
                    break
                else:
                    if not region_pos:
                        return None
                    x, y = region_pos.pop()
    return None

def solve_952a094c(img: Image):
    region = Region(img).region_info
    box_ri = [ri for ri in region if ri.size > 1 and ri.color != img.background_color]
    assert len(box_ri) == 1
    box_ri = box_ri[0]
    corners = box_ri.corners()
    opposite_corners = [3, 2, 1, 0]
    for i in range(4):
        (tx, ty), (dx, dy) = corners[opposite_corners[i]]
        tx, ty = tx + dx, ty + dy
        (sx, sy), (dx, dy) = corners[i]
        sx, sy = sx - dx, sy - dy
        img[tx, ty] = img[sx, sy]
        img[sx, sy] = img.background_color
    return img

def solve_0b148d64(img: Image):
    region_info = Region(img).region_info
    region_info = combine_regions_in_box(region_info)
    region_info = [ri for ri in region_info if ri.color != img.background_color]
    region_color_count = {}
    for ri in region_info:
        if ri.color not in region_color_count:
            region_color_count[ri.color] = 0
        region_color_count[ri.color] += 1
    single_color_regions = [ri for ri in region_info if region_color_count[ri.color] == 1]
    assert len(single_color_regions) == 1
    return img.subimage_of_region(single_color_regions[0])

def predict_output_size(data: Data):
    # constant:
    shape = data.train[0].output.shape
    if all([s.output.shape == shape for s in data.train]):
        return shape
    # same with input:
    if all([s.input.shape == s.output.shape for s in data.train]):
        return [s.input.shape for s in data.test]
    # same with some region:
    return None


def test_single_prediction(k):
    from data import get_data
    data = get_data(True)[k]
    print(f"test on {k}")
    region_bool_prediction(data.train)

if __name__ == '__main__':
    move_ks = ['05f2a901', '2dc579da',
        'be94b721', 'a87f7484',
        '1f85a75f', 'a61ba2ce', '72ca375d', 'beb8660c', '23b5c85d',
        '25ff71a9', '1caeab9d', '1cf80156', 'd89b689b', 'ce602527',
        '5521c0d9', 'dc433765']
    rectangle_region_ks = ['98cf29f8']
    paint_ks = ['3bdb4ada', 'ea786f4a', '4347f46a']
    # test_all(move_ks[1])

    for k in move_ks:
        test_single_prediction(k)
