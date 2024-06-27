from region import Region
from data import Data

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

def resize(x, y, scale):
    return x * scale, y * scale

def rotate(x, y, type):
    if type == 0:
        return x, y
    elif type == 1:
        return -x, y
    elif type == 2:
        return x, -y
    elif type == 3:
        return -x, -y
    elif type == 4:
        return y, x
    elif type == 5:
        return -y, x
    elif type == 6:
        return y, -x
    elif type == 7:
        return -y, -x


def find_position_map(data: Data):
    patterns = []
    for s in data.train:
        if s.input.background_color != s.output.background_color:
            print("background color not match")
            s.output.background_color = s.input.background_color
        cs = s.output.color_set.union(s.input.color_set)
        # print(cs)
        ips = [same_color_set(s.input, c) for c in cs]
        ips = [[rotate(x, y, 0) for x, y in ip] for ip in ips]
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
        target_region = target_region.region
        region_map = {}
        # 每个位置其实可以不止有一个偏移
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j] == img.background_color:
                    continue
                dts = set([(i - ip[0], j - ip[1]) for ip in ips[cis[img[i, j]]]])
                if target_region[i, j] not in region_map:
                    region_map[target_region[i, j]] = dts
                else:
                    region_map[target_region[i, j]] = region_map[target_region[i, j]].intersection(dts)
        target_region_offsets = []
        for i in range(len(target_region_info)):
            if target_region_info[i].color == img.background_color:
                target_region_offsets.append((0, 0))
                continue
            if len(region_map[i]) != 1:
                print(f"region {i} has {len(region_map[i])} offsets")
                return
            else:
                target_region_offsets.append(region_map[i].pop())
        assert len(target_region_offsets) == len(target_region_info)
        if DEBUG: print('target region offsets', target_region_offsets)

        input_region = Region(s.input).region_info
        input_region = [r for r in input_region if r.color != img.background_color]
        input_region_offsets = [[] for _ in range(len(input_region))]
        for i in range(len(target_region_info)):
            if target_region_info[i].color == img.background_color:
                continue
            target = target_region_info[i]
            for j in range(len(input_region)):
                source = input_region[j]
                offset = (target.top - source.top, target.left - source.left)
                if offset == target_region_offsets[i]:
                    input_region_offsets[j].append(offset)
        if DEBUG: print('input region offsets', input_region_offsets)
        if all([len(offsets) <= 1 for offsets in input_region_offsets]):
            if DEBUG: print("Found Move Pattern.")
            for i in range(len(input_region)):
                if len(input_region_offsets[i]) != 1:
                    continue
                gt_offset = input_region_offsets[i][0]
                input_patten = [input_region[i]]
                for j in range(len(input_region)):
                    if i != j:
                        input_patten.append(input_region[j])
                patterns.append((input_patten, gt_offset))
        else:
            print("Found Copy Pattern.")
    return patterns


if __name__ == '__main__':
    from data import get_data
    from concept import *
    from reasoning import *
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
        patterns = find_position_map(data)
        if patterns:
            print(patterns)
