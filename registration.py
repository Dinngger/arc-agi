
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


if __name__ == '__main__':
    from data import *
    from concept import *
    from reasoning import *
    data = get_data(True)['72322fa7']
    for s in data.train:
        cs = s.output.color_set().union(s.input.color_set())
        cs.remove(0)
        print(cs)
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
        # 每个位置其实可以不止有一个偏移
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j] == 0:
                    print('_', end=' ')
                    continue
                max_cnt = 0
                max_dt = None
                for ip in ips[cis[img[i, j]]]:
                    dt = (i - ip[0], j - ip[1])
                    if ts[dt] > max_cnt:
                        max_cnt = ts[dt]
                        max_dt = dt
                print(max_dt, end=' ')
            print()
