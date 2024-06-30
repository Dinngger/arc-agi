import numpy as np
from typing import List
from region import Region, RegionInfo
from data import Image, Sample, Data
from registration import find_position_map
from decision_tree import Node
from celer import Lasso


def remove_move_region(img: Image, region: Region, offsets):
    res = img.copy()
    for idx in range(region.num):
        ri = region.region_info[idx]
        if offsets[idx] and offsets[idx][0] != (0, 0):
            for i in range(ri.top, ri.bottom + 1):
                for j in range(ri.left, ri.right + 1):
                    if region.region[i, j] == idx:
                        res[i, j] = img.background_color
    return res

def unique_pattern(img: Image, i0, j0):
    pattern = img.pattern3x3(i0, j0)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if i != i0 or j != j0:
                if img.pattern3x3(i, j) == pattern:
                    print(f"pattern {pattern} from {i0, j0} is not unique at {i, j}")
                    return False
    return True

def find_pattern(img: Image, pattern):
    pos = []
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img.pattern3x3(i, j) == pattern:
                pos.append((i, j))
    return pos

def learn_move_pattern(samples: List[Sample]):
    pattern_x = []
    pattern_y = []
    for s in samples:
        region = Region(s.input)
        offset = find_position_map(s)
        if offset is None:
            return
        img = remove_move_region(s.input, region, offset)
        # pick a 3x3 region to judge
        for i in range(region.num):
            if offset[i] and offset[i][0] != (0, 0):
                if len(offset[i]) != 1:
                    return
                dx, dy = offset[i][0]
                ri = region.region_info[i]
                if not unique_pattern(img, ri.top, ri.left):
                    return
                if not unique_pattern(img, ri.top + dx, ri.left + dy):
                    return
                pattern_x.append(img.pattern3x3(ri.top, ri.left))
                pattern_y.append(img.pattern3x3(ri.top + dx, ri.left + dy))
    if not pattern_y:
        return
    pattern_x = np.array(pattern_x)
    pattern_y = np.array(pattern_y)
    nodes = []
    for i in range(9):
        node_i = Node(pattern_x, pattern_y[:, i])
        assert node_i.split() is not None
        nodes.append(node_i)
    return nodes

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


def find_target_pattern(img: Image, nodes: List[Node]):
    region = Region(img)
    static_regions = img.copy()
    for idx in range(region.num):
        ri = region.region_info[idx]
        if ri.size == 1:
            static_regions[ri.top, ri.left] = img.background_color
    res = static_regions.copy()
    for idx in range(region.num):
        ri = region.region_info[idx]
        if ri.size == 1:
            pattern = [node.predict(img.pattern3x3(ri.top, ri.left)) for node in nodes]
            pos = find_pattern(static_regions, pattern)
            assert len(pos) == 1
            res[pos[0]] = img[ri.top, ri.left]
    return res

def paint_region(img: Image, region: RegionInfo, dx, dy):
    for x0, y0 in region.pixels:
        x = x0 + dx - region.top
        y = y0 + dy - region.left
        if x < 0 or x >= img.shape[0] or y < 0 or y >= img.shape[1]:
            return False
        if img[x, y] != img.background_color:
            return False
        img[x, y] = region.color
    return True

def try_paint_region(img: Image):
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

def move_solver(data: Data):
    nodes = learn_move_pattern(data.train)
    if nodes is None:
        print('pattern not found')
        return None
    return lambda x: find_target_pattern(x, nodes)

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


class RegionMap:
    @staticmethod
    def fit(samples: List[Sample]):
        pass


def test_single_prediction(k):
    from data import get_data
    data = get_data(True)[k]
    print(f"test on {k}")
    region_bool_prediction(data.train)

def test_all(k):
    from data import get_data
    datas = get_data(True)
    data = datas[k]
    for s in data.train:
        pred = try_paint_region(s.input)
        if pred != s.output:
            print('fail on ', k)
            print('pred')
            print(pred)
            print('ground truth')
            print(s.output)
            break
    for s in data.test:
        pred = try_paint_region(s.input)
        if pred != s.output:
            print('fail on ', k)
            print('pred')
            print(pred)
            print('ground truth')
            print(s.output)
            break
    print('success on ', k)


if __name__ == '__main__':
    move_ks = ['952a094c', '681b3aeb', '05f2a901', '2dc579da',
        'be94b721', 'a87f7484',
        '1f85a75f', 'a61ba2ce', '72ca375d', 'beb8660c', '23b5c85d',
        '25ff71a9', '1caeab9d', '1cf80156', 'd89b689b', 'ce602527',
        '5521c0d9', 'dc433765']
    rectangle_region_ks = ['98cf29f8']
    paint_ks = ['3bdb4ada', 'ea786f4a', '4347f46a']
    # test_all(move_ks[1])

    for k in move_ks:
        test_single_prediction(k)
