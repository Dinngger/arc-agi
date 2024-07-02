from enum import Enum
from region import Region
from data import Sample, Image

DEBUG = False
"""find correct position map logic, include Resize, Rotate, Mirror, Translate."""
# Use Hough Transform !!!

def same_color_set(img, color):
    res = []
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] == color:
                res.append((i, j))
    return res

class RotateType(Enum):
    Nothing = 0
    UpDown = 1
    LeftRight = 2
    Center = 3      # same with rotate 180 degree
    Diagonal = 4
    Right = 5
    Left = 6
    AntiDiagonal = 7

rigid_rotate_types = [RotateType.Nothing, RotateType.Left, RotateType.Right, RotateType.Center]

def transform(x, y, type, scale=1, dx=0, dy=0):
    if type == RotateType.Nothing:
        return x * scale + dx, y * scale + dy
    elif type == RotateType.UpDown:
        return -x * scale + dx, y * scale + dy
    elif type == RotateType.LeftRight:
        return x * scale + dx, -y * scale + dy
    elif type == RotateType.Center:
        return -x * scale + dx, -y * scale + dy
    elif type == RotateType.Diagonal:
        return y * scale + dx, x * scale + dy
    elif type == RotateType.Right:
        return -y * scale + dx, x * scale + dy
    elif type == RotateType.Left:
        return y * scale + dx, -x * scale + dy
    elif type == RotateType.AntiDiagonal:
        return -y * scale + dx, -x * scale + dy


def find_position_map(s: Sample):
    if s.input.background_color != s.output.background_color:
        if DEBUG: print("background color not match")
        s.output.background_color = s.input.background_color
    cs = s.output.color_set.union(s.input.color_set)
    # print(cs)
    ips = [same_color_set(s.input, c) for c in cs]
    ips = [[transform(x, y, RotateType.Nothing) for x, y in ip] for ip in ips]
    ops = [same_color_set(s.output, c) for c in cs]
    ts = {}
    # 计算偏移的频率
    for ci in range(len(cs)):
        for op in ops[ci]:
            for ip in ips[ci]:
                dt = (op[0] - ip[0], op[1] - ip[1])
                if dt not in ts:
                    ts[dt] = 1
                else:
                    ts[dt] += 1
    img = s.output
    # 颜色索引表
    cis = {}
    for ci, c in zip(range(len(cs)), cs):
        cis[c] = ci
    # 找出最可能的偏移，应结合Region
    target_region = Region(img)
    target_region_info = target_region.region_info
    target_region_img = target_region.region
    region_map = {}
    # 每个位置其实可以不止有一个偏移
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] == img.background_color:
                continue
            dts = set([(i - ip[0], j - ip[1]) for ip in ips[cis[img[i, j]]]])
            if target_region_img[i, j] not in region_map:
                region_map[target_region_img[i, j]] = dts
            else:
                region_map[target_region_img[i, j]] = region_map[target_region_img[i, j]].intersection(dts)
    target_region_offsets = []
    for i in range(target_region.num):
        if target_region_info[i].color == img.background_color:
            target_region_offsets.append((0, 0))
            continue
        if len(region_map[i]) != 1:
            if DEBUG: print(f"region {i} has {len(region_map[i])} offsets")
            return
        else:
            target_region_offsets.append(region_map[i].pop())
    assert len(target_region_offsets) == target_region.num
    if DEBUG: print('target region offsets', target_region_offsets)

    input_region = Region(s.input)
    input_region_offsets = [[] for _ in range(input_region.num)]
    for i in range(target_region.num):
        if target_region_info[i].color == img.background_color:
            continue
        target = target_region_info[i]
        for j in range(input_region.num):
            if input_region.region_info[j].color == img.background_color:
                continue
            source = input_region.region_info[j]
            offset = (target.top - source.top, target.left - source.left)
            if offset == target_region_offsets[i]:
                input_region_offsets[j].append(offset)
    return input_region_offsets


def test_find_position_map():
    from data import get_data
    datas = get_data(True)
    ks = ['952a094c', '681b3aeb', '05f2a901', '2dc579da', '3bdb4ada',
          'be94b721', 'ea786f4a', '4347f46a', '98cf29f8', 'a87f7484',
          '1f85a75f', 'a61ba2ce', '72ca375d', 'beb8660c', '23b5c85d',
          '25ff71a9', '1caeab9d', '1cf80156', 'd89b689b', 'ce602527',
          '5521c0d9', 'dc433765']   # all move patterns
    # for k, data in datas.items():
    for k in ks:
        data = datas[k]
        print(k, end=' ')
        for s in data.train:
            input_region_offsets = find_position_map(s)
            if input_region_offsets:
                print(input_region_offsets)


def solve_7df24a62(img: Image):
    region = Region(img)
    for ri in region.region_info:
        if ri.color == 1:
            template_ri = ri
            break
    template = [(x, y) for x in range(template_ri.top, template_ri.bottom+1)
                       for y in range(template_ri.left, template_ri.right+1)
                       if img[x, y] == 4]
    res = img.copy()
    for ri in region.region_info:
        if ri.color != 4:
            continue
        for x, y in ri.pixels:
            for x0, y0 in template:
                for rt in rigid_rotate_types:
                    tx0, tx1 = transform(x0, y0, rt)
                    dx, dy = x - tx0, y - tx1
                    for x1, y1 in template:
                        if img[transform(x1, y1, rt, 1, dx, dy)] != 4:
                            break
                    else:
                        for x2, y2 in template_ri.pixels:
                            tx2, ty2 = transform(x2, y2, rt, 1, dx, dy)
                            if res.in_bound(tx2, ty2) and res[tx2, ty2] == 0:
                                res[tx2, ty2] = 1
    return res


def test_solvers():
    from data import get_data
    datas = get_data(True)
    easy_ks = ['7df24a62']
    for k in easy_ks:
        solver = globals()[f'solve_{k}']
        data = datas[k]
        for s in data.train:
            pred = solver(s.input)
            if pred != s.output:
                print('fail on ', k)
                print('pred')
                print(pred)
                print('ground truth')
                print(s.output)
                break
        for s in data.test:
            pred = solver(s.input)
            if pred != s.output:
                print('fail on ', k)
                print('pred')
                print(pred)
                print('ground truth')
                print(s.output)
                break
        print('success on ', k)

if __name__ == '__main__':
    test_solvers()
