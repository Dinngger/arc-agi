from data import *
from region import Region, RegionInfo
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
    region = Region(img).region_info
    region = [ri for ri in region if ri.color == 2]
    n = len(region)
    for i in range(n):
        for j in range(i+1, n):
            xsi = set(range(region[i].top, region[i].bottom+1))
            xsj = set(range(region[j].top, region[j].bottom+1))
            common_x = xsi & xsj
            if len(common_x) == 0:
                continue
            if region[i].left < region[j].left:
                common_y = list(range(region[i].right+1, region[j].left))
            else:
                common_y = list(range(region[j].right+1, region[i].left))
            for x, y in [(x, y) for x in common_x for y in common_y]:
                if img[x, y] != 0:
                    break
            else:
                for x, y in [(x, y) for x in common_x for y in common_y]:
                    img[x, y] = 9
    return img

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
    region = Region(img).region_info
    res = Image.zeros(img.shape)
    for outer in [ri for ri in region if ri.level == 1]:
        inner = [ri for ri in region if ri.level == 2 and ri.in_region_box(outer)]
        assert len(inner) == 1
        inner = inner[0]
        outer.paint_on(res, color=inner.color)
        inner.paint_on(res, color=outer.color)
        assert inner.width == inner.width
        width = inner.width
        RegionInfo.box_region(outer.top - width, outer.left, outer.top-1, outer.right, outer.color).paint_on(res)
        RegionInfo.box_region(outer.top, outer.left - width, outer.bottom, outer.left-1, outer.color).paint_on(res)
        RegionInfo.box_region(outer.bottom+1, outer.left, outer.bottom+width, outer.right, outer.color).paint_on(res)
        RegionInfo.box_region(outer.top, outer.right+1, outer.bottom, outer.right+width, outer.color).paint_on(res)
    return res

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

def solve_ff805c23(img: Image):
    unknown = RegionInfo.from_color(img, 1)
    res = Image.zeros((unknown.heigth, unknown.width))
    cx, cy = img.center()
    for x, y in unknown.pixels:
        for t in [RotateType.LeftRight, RotateType.UpDown]:
            ti, tj = transform(x - cx, y - cy, t)
            ti, tj = cx + ti, cy + tj
            if img.in_bound(int(ti), int(tj)) and img[int(ti), int(tj)] != 1:
                res[x - unknown.top, y - unknown.left] = img[int(ti), int(tj)]
                break
    return res

def solve_e8593010(img: Image):
    region = Region(img, strict_neighbour=True)
    for ri in region.region_info:
        if ri.color == 0:
            c = 4 - ri.size
            for i, j in ri.pixels:
                img[i, j] = c
    return img

def find_minimal_repetitive_pattern(seq):
    for cycle in range(1, len(seq) + 1):
        if all(seq[i] == seq[i % cycle] for i in range(len(seq))):
            return cycle
    raise ValueError("No minimal repetitive pattern found.")

def solve_017c7c7b(img: Image):
    cycle = find_minimal_repetitive_pattern(img.list)
    return Image.generate(lambda i, j: 2 if img[i % cycle, j] else 0, (9, 3))

def solve_ec883f72(img: Image):
    region = Region(img).region_info
    ris = [ri for ri in region if ri.level != 0]
    inner = min(ris, key=lambda ri: ri.heigth * ri.width)
    outer = max(ris, key=lambda ri: ri.heigth * ri.width)
    c = inner.color
    for (cx, cy), (dx, dy) in outer.corners():
        cx, cy = cx + dx, cy + dy
        while img.in_bound(cx, cy):
            img[cx, cy] = c
            cx, cy = cx + dx, cy + dy
    return img

def solve_150deff5(img: Image):
    region = RegionInfo.from_color(img, 5)
    draw_types = [0]
    draw_colors = {0: 8, 1: 2, 2: 2}
    draw_pos = {0: [(0, 0), (0, 1), (1, 0), (1, 1)],
                1: [(0, 0), (0, 1), (0, 2)],
                2: [(0, 0), (1, 0), (2, 0)]}
    def draw_next(i: Image, t):
        for x, y in region.pixels:
            if i[x, y] == 5:
                if all([i[x+dx, y+dy] == 5 for dx, dy in draw_pos[t]]):
                    for dx, dy in draw_pos[t]:
                        i[x+dx, y+dy] = draw_colors[t]
                    return 1
                else:
                    return -1
        return 0
    while draw_types:
        t = draw_types.pop()
        res = img.copy()
        for ti in draw_types:
            assert draw_next(res, ti) == 1
        r = draw_next(res, t)
        if r == 1:
            draw_types.append(t)
            draw_types.append(0)
        elif r == 0:
            return res
        else:
            while True:
                if t < 2:
                    draw_types.append(t+1)
                    break
                else:
                    if not draw_types:
                        return None
                    t = draw_types.pop()
    return None

def solve_56dc2b01(img: Image):
    line = RegionInfo.from_color(img, 2)
    new_line = line.copy()
    new_line.color = 8
    shape = RegionInfo.from_color(img, 3)
    dir_x = img.shape[0] > img.shape[1]
    res = Image.zeros(img.shape)
    line.paint_on(res)
    if dir_x:
        if line.top < shape.top:
            shape.paint_on(res, line.top - shape.top + 1, 0)
            new_line.paint_on(res, shape.heigth + 1, 0)
        else:
            shape.paint_on(res, line.top - shape.bottom - 1, 0)
            new_line.paint_on(res, -shape.heigth - 1, 0)
    else:
        if line.left < shape.left:
            shape.paint_on(res, 0, line.left - shape.left + 1)
            new_line.paint_on(res, 0, shape.width + 1)
        else:
            shape.paint_on(res, 0, line.left - shape.right - 1)
            new_line.paint_on(res, 0, -shape.width - 1)
    return res

def solve_aabf363d(img: Image):
    c = img[img.height-1, 0]
    img[img.height-1, 0] = 0
    for i in range(img.height):
        for j in range(img.width):
            if img[i, j] != 0:
                img[i, j] = c
    return img

def solve_ba97ae07(img: Image):
    cs = img.color_set
    cs.remove(0)
    ris = [RegionInfo.from_color(img, c) for c in cs]
    ris = [ri for ri in ris if not ri.full_of_box()]
    assert len(ris) == 1
    ri = ris[0]
    for i in range(ri.top, ri.bottom+1):
        for j in range(ri.left, ri.right+1):
            img[i, j] = ri.color
    return img

def solve_05269061(img: Image):
    cs = img.color_set
    cs.remove(0)
    n = len(cs)
    color_table = [None, None, None]
    for i in range(img.height):
        for j in range(img.width):
            if img[i, j] != 0:
                idx = (i + j) % n
                if color_table[idx] is None:
                    color_table[idx] = img[i, j]
                else:
                    assert color_table[idx] == img[i, j]
    for i in range(img.height):
        for j in range(img.width):
            img[i, j] = color_table[(i + j) % n]
    return img

def solve_7ddcd7ec(img: Image):
    region = Region(img, strict_neighbour=True).region_info
    ris = [ri for ri in region if ri.size == 4]
    assert len(ris) == 1
    box = ris[0]
    for (x, y), (dx, dy) in box.corners():
        if img[x+dx, y+dy] != 0:
            while img.in_bound(x+dx, y+dy):
                img[x+dx, y+dy] = box.color
                x, y = x+dx, y+dy
    return img
