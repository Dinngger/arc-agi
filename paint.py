from data import *
from region import Region
from registration import RotateType, transform

def solve_5c2c9af4(img: Image):
    region = Region(img)
    region_info = region.region_info
    for ri in region_info:
        if ri.size == 1:
            paint_color = ri.color
            break
    three_points = [ri.pixels[0] for ri in region_info if ri.size == 1]
    three_points.sort(key=lambda p: p[0])
    middle_point = three_points[1]
    x, y = middle_point
    d = abs(three_points[0][0] - x)
    def f(i, j):
        dx = abs(i - x)
        dy = abs(j - y)
        if dx < dy:
            dx, dy = dy, dx
        if dx % d == 0:
            return paint_color
        else:
            return img.background_color
    return img.generate(f, img.shape)

def find_nonzero(img: Image, i, j, di, dj, zero=0, num=1, return_pos=False, return_dist=False):
    dist = 0
    while img.in_bound(i, j):
        i += di
        j += dj
        dist += 1
        if img[i, j] != zero:
            for k in range(num-1):
                i += di
                j += dj
                if not img.in_bound(i, j) or img[i, j] == zero:
                    return 0 if zero == 0 else None
            if return_dist:
                return dist
            elif return_pos:
                return (i, j)
            else:
                return img[i, j]
    return 0 if zero == 0 else None

def solve_ef135b50(img: Image):
    def f(i, j):
        if img[i, j] == 2:
            return 2
        if find_nonzero(img, i, j, 0, -1) != 0 and find_nonzero(img, i, j, 0, 1) != 0:
            return 9
        return 0
    return img.generate(f, img.shape)

def solve_623ea044(img: Image):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] != 0:
                x0, y0 = i, j
                c = img[i, j]
                break
    def f(i, j):
        dx = abs(i - x0)
        dy = abs(j - y0)
        if dx == dy:
            return c
        else:
            return 0
    return img.generate(f, img.shape)

def solve_dbc1a6ce(img: Image):
    def f(i, j):
        if img[i, j] == 1:
            return 1
        if find_nonzero(img, i, j, -1, 0) != 0 and find_nonzero(img, i, j, 1, 0) != 0:
            return 8
        if find_nonzero(img, i, j, 0, -1) != 0 and find_nonzero(img, i, j, 0, 1) != 0:
            return 8
        return 0
    return img.generate(f, img.shape)

def solve_bdad9b1f(img: Image):
    def f(i, j):
        if img[i, j] != 0:
            return img[i, j]
        a = find_nonzero(img, i, j, -1, 0, num=2) or find_nonzero(img, i, j, 1, 0, num=2)
        b = find_nonzero(img, i, j, 0, -1, num=2) or find_nonzero(img, i, j, 0, 1, num=2)
        if a and b:
            return 4
        elif a:
            return a
        elif b:
            return b
        else:
            return 0
    return img.generate(f, img.shape)

def solve_1e0a9b12(img: Image):
    res = Image.zeros(img.shape)
    for j in range(img.shape[1]):
        now_i = img.shape[0] - 1
        for i in range(img.shape[0], -1, -1):
            if img[i, j] != 0:
                res[now_i, j] = img[i, j]
                now_i -= 1
    return res

def solve_a48eeaf7(img: Image):
    res = img.copy()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] == 5:
                res[i, j] = 0
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if find_nonzero(img, i, j, dx, dy) == 2:
                        x, y = find_nonzero(img, i, j, dx, dy, return_pos=True)
                        res[x - dx, y - dy] = 5
                        break
    return res

def solve_3befdf3e(img: Image):
    region = Region(img)
    for ri in region.region_info:
        if ri.level == 1:
            outer_color = ri.color
        elif ri.level == 2:
            inner_color = ri.color
            inner_width = ri.bottom - ri.top + 1
    def f(i, j):
        if img[i, j] == outer_color:
            return inner_color
        if img[i, j] == inner_color:
            return outer_color
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if find_nonzero(img, i, j, dx, dy) == outer_color:
                x, y = find_nonzero(img, i, j, dx, dy, return_pos=True)
                if abs(i - x) + abs(j - y) <= inner_width:
                    return outer_color
        return 0
    return img.generate(f, img.shape)

def solve_bda2d7a6(img: Image):
    region = Region(img)
    colors = {ri.level: ri.color for ri in region.region_info}
    color_map = {}
    for l, c in colors.items():
        if l != 0:
            color_map[c] = colors[l-1]
    if colors[0] not in color_map:
        color_map[colors[0]] = colors[len(colors)-1]
    return img.generate(lambda i, j: color_map[img[i, j]], img.shape)

def solve_f35d900a(img: Image):
    c1, c2 = [c for c in img.color_set if c != 0]
    def f(i, j):
        if img[i, j] != 0:
            return img[i, j]
        neighbor = [c for c in img.pattern3x3(i, j) if c != 0]
        if neighbor:
            return c1 if neighbor[0] == c2 else c2
        a = find_nonzero(img, i, j, -1, 0, return_dist=True)
        b = find_nonzero(img, i, j, 1, 0, return_dist=True)
        c = find_nonzero(img, i, j, 0, -1, return_dist=True)
        d = find_nonzero(img, i, j, 0, 1, return_dist=True)
        dist = 0
        if a != 0 and b != 0:
            dist = min(a, b)
        elif c != 0 and d != 0:
            dist = min(c, d)
        if dist != 0:
            return 5 if dist % 2 == 0 else 0
        return 0
    return img.generate(f, img.shape)

def solve_264363fd(img: Image):
    assert img.background_color == img[0, 0]
    region = Region(img)
    l1ri = region.hierarchical_region_infos[1]
    canvases = [ri for ri in l1ri if ri.size >= 25]
    template = [ri for ri in l1ri if ri.size < 25]
    assert len(template) == 1
    template = template[0]
    tx, ty = template.center()
    locate_color = img[tx, ty]
    search_dirs = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        if img[tx - dx * 2, ty - dy * 2] != img.background_color:
            search_dirs.append((dx, dy))
            search_color = img[tx - dx * 2, ty - dy * 2]
    canvases_img = [img.subimage(ri.top, ri.left, ri.bottom, ri.right) for ri in canvases]
    def f(img, i, j):
        for dx, dy in search_dirs:
            if find_nonzero(img, i, j, dx, dy, zero=img.background_color):
                return search_color
        return img[i, j]
    canvases_img = [canvas.self_generate(f) for canvas in canvases_img]
    for ri, canvas in zip(canvases, canvases_img):
        for i in range(canvas.shape[0]):
            for j in range(canvas.shape[1]):
                if img[i+ri.top, j+ri.left] == locate_color:
                    for ti, tj in template.pixels:
                        if canvas.in_bound(i+ti-tx, j+tj-ty):
                            canvas[i+ti-tx, j+tj-ty] = img[ti, tj]
    res = Image.generate(lambda i, j: img.background_color, img.shape)
    for ri, canvas in zip(canvases, canvases_img):
        for i in range(ri.top, ri.bottom+1):
            for j in range(ri.left, ri.right+1):
                res[i, j] = canvas[i-ri.top, j-ri.left]
    return res

def solve_c9f8e694(img: Image):
    def f(i, j):
        if img[i, j] != 5:
            return img[i, j]
        return img[i, 0]
    return img.generate(f, img.shape)

def solve_60b61512(img: Image):
    for ri in Region(img).region_info:
        if ri.level == 0:
            continue
        for i in range(ri.top, ri.bottom+1):
            for j in range(ri.left, ri.right+1):
                if img[i, j] == 0:
                    img[i, j] = 7
    return img

def solve_f8b3ba0a(img: Image):
    region = Region(img).region_info
    colors = [ri.color for ri in region if ri.level != 0]
    color_count = {}
    for c in colors:
        color_count[c] = color_count.get(c, 0) + 1
    assert len(color_count) == 4
    color_sort = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
    cs = [[c[0]] for c in color_sort]
    return Image(cs[1:])

def solve_4938f0c2(img: Image):
    region = Region(img)
    for ri in region.region_info:
        if ri.color == 3:
            center = ri
            break
    cx, cy = center.center(strict=False)
    for i in range(ri.top):
        for j in range(ri.left):
            if img[i, j] != 0:
                for t in [RotateType.LeftRight, RotateType.UpDown, RotateType.Center]:
                    ti, tj = transform(i - cx, j - cy, t)
                    img[int(cx + ti), int(cy + tj)] = 2
    return img

def solve_d406998b(img: Image):
    for j in range(img.shape[1]):
        nj = img.shape[1] - 1 - j
        for i in range(img.shape[0]):
            if img[i, nj] != 0 and j % 2 == 0:
                img[i, nj] = 3
    return img

def solve_868de0fa(img: Image):
    region = Region(img)
    for ri in region.region_info:
        if ri.level == 2:
            assert ri.width == ri.heigth
            if ri.width % 2 == 0:
                c = 2
            else:
                c = 7
            for i in range(ri.top, ri.bottom+1):
                for j in range(ri.left, ri.right+1):
                    img[i, j] = c
    return img

if __name__ == '__main__':
    easy_ks = ['5c2c9af4', '623ea044', 'dbc1a6ce', 'bdad9b1f', '1e0a9b12',
               'a48eeaf7', 'bda2d7a6', 'f35d900a', '264363fd', 'c9f8e694',
               '60b61512', 'f8b3ba0a', '4938f0c2', 'd406998b', '868de0fa']
    hard_ks = ['ef135b50', '3befdf3e']
    datas = get_data(True)
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
