import os
import random
import json
from collections import Counter
from dataclasses import dataclass
from typing import List
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib import colors
from tqdm import tqdm

def get_data(name):
    path = f'../ARC-AGI/data/training/{name}.json'
    with open(path, 'r') as f:
        data = json.load(f)
    return data['train']

all_files = os.listdir('../ARC-AGI/data/training/')
random_file = random.choice(all_files)
name = random_file.split('.')[0]
print(name)

cmap = colors.ListedColormap(
    ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
    '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25', '#FFFFFF'])
norm = colors.Normalize(vmin=0, vmax=10)

imgs = get_data(name)
img = imgs[0]['output']

def draw_img(ax: plt.Axes, img):
    ax.imshow(img, cmap=cmap, norm=norm)
    ax.grid(True,which='both',color='lightgrey', linewidth=0.5)
    ax.set_yticks([x-0.5 for x in range(1+len(img))])
    ax.set_xticks([x-0.5 for x in range(1+len(img[0]))])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

def show_imgs(imgs):
    n = len(imgs)
    for i, io in enumerate(imgs):
        ax = plt.subplot(n, 2, i*2+1)
        draw_img(ax, io['input'])
        ax = plt.subplot(n, 2, i*2+2)
        draw_img(ax, io['output'])
    plt.show()

regions = []
@dataclass
class Pos:
    x: int
    y: int
    def __sub__(self, value) -> 'Pos':
        return Pos(self.x - value.x, self.y - value.y)
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    def norm(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
@dataclass
class Region:
    pos: Pos
    components: List['Region']
    id: int
    def __eq__(self, value) -> bool:
        return self.id == value.id
    def __hash__(self) -> int:
        return hash(self.id)
    def __repr__(self) -> str:
        return str(self.id)
    def get_pixels(self):
        if not self.components:
            return [(self.pos, self.id)]
        pixels = []
        for c in self.components:
            pixels.extend(c.get_pixels())
        return pixels
    def plot(self, ax):
        pixels = self.get_pixels()
        min_x = min(p[0].x for p in pixels)
        min_y = min(p[0].y for p in pixels)
        height = max(p[0].x for p in pixels) - min_x + 1
        width = max(p[0].y for p in pixels) - min_y + 1
        list = [[10 for _ in range(width)] for _ in range(height)]
        for p in pixels:
            list[p[0].x - min_x][p[0].y - min_y] = p[1]
        ax.imshow(list, cmap=cmap, norm=norm)
        ax.grid(True,which='both',color='lightgrey', linewidth=0.5)
        ax.set_yticks([x-0.5 for x in range(1+height)])
        ax.set_xticks([x-0.5 for x in range(1+width)])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_title(f'region{self.id}')
@dataclass
class Pair:
    region1: Region
    region2: Region
    relative_pos: Pos
    def __init__(self, region1: Region, region2: Region):
        self.region1 = region1
        self.region2 = region2
        self.relative_pos = region2.pos - region1.pos
    def __hash__(self) -> int:
        return hash((self.region1, self.region2, self.relative_pos))
    # def __eq__(self, value) -> bool:
for i in range(len(img)):
    for j in range(len(img[i])):
        if img[i][j] != 0:
            regions.append(Region(Pos(i, j), [], img[i][j]))
def neighbor(ra: Region, rb: Region) -> bool:
    pa = ra.get_pixels()
    pb = rb.get_pixels()
    for p in pa:
        for q in pb:
            if (p[0] - q[0]).norm() < 1.5:
                return True
    return False
min_lp = None
stop = False
sub_regions = []
def ladderpath(s, cnt=0):
    global min_lp, stop
    # if cnt > 20:
        # stop = True
    if stop:
        return
    all_2_grams = [Pair(s[i], s[j]) for i in range(len(s)) for j in range(len(s)) if i != j and neighbor(s[i], s[j])]
    count = Counter(all_2_grams)
    count = sorted(count.items(), key=lambda x: x[1], reverse=True)
    count = [k for k,v in count if v > 1]
    # print(cnt, len(count))
    # print(s)
    if not count:
        if min_lp is None:
            min_lp = len(s) + cnt
            print('min_lp', min_lp)
            stop = True
        else:
            if len(s) + cnt < min_lp:
                print('min_lp', len(s) + cnt)
            min_lp = min(min_lp, len(s) + cnt)
        # print('min_lp', min_lp)
    for k in count:
        new_s = []
        removed_region = []
        # print(f"replace {k} with {-cnt-1}")
        sub_regions.append(Region(k.region1.pos, [k.region1, k.region2], -cnt-1))
        for i in range(len(s)):
            if i in removed_region:
                continue
            for j in range(len(s)):
                if j in removed_region or i == j:
                    continue
                if Pair(s[i], s[j]) == k:
                    new_s.append(Region(s[i].pos, [s[i], s[j]], -cnt-1))
                    removed_region.extend([i, j])
                    break
        for i in range(len(s)):
            if i not in removed_region:
                new_s.append(s[i])
        ladderpath(new_s, cnt+1)
        if stop:
            return
ladderpath(regions)
n = len(sub_regions)
h = w = int(n ** 0.5)
if h * w < n:
    h += 1
if h * w < n:
    w += 1
assert n <= h * w
for i in range(n):
    sub_regions[i].plot(plt.subplot(h, w*2, (i // w) * (w*2) + i % w + 1))
ax = plt.subplot(1, 2, 2)
ax.imshow(img, cmap=cmap, norm=norm)
ax.grid(True,which='both',color='lightgrey', linewidth=0.5)
ax.set_yticks([x-0.5 for x in range(1+len(img))])
ax.set_xticks([x-0.5 for x in range(1+len(img[0]))])
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_title(f'img lp={min_lp}')
plt.show()
