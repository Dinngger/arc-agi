import os
import json
import random
from datatypes import *


path = '../../ARC-AGI/data/training'
fn = random.choice(os.listdir(path))
with open(f'{path}/{fn}') as f:
    data = json.load(f)
ns = len(data['train'])
samples: List[Tuple[Image, Image]] = []
for sample in data['train']:
    img_input = Image(sample['input'])
    img_output = Image(sample['output'])
    samples.append((img_input, img_output))

print("IO shapes:")
for i, o in samples:
    print(i.shape, o.shape)
if not all(i.shape == o.shape for i, o in samples):
    os._exit(0)

print("Color count:")
def count_img_color(img):
    color_count = {}
    for row in img.list:
        for x in row:
            if x not in color_count:
                color_count[x] = 0
            color_count[x] += 1
    return color_count
color_counts = []
for i, o in samples:
    ic = count_img_color(i)
    oc = count_img_color(o)
    print(ic, '->', oc)
    color_counts.append((ic, oc))


if all(0 in ic and 0 in oc for ic, oc in color_counts):
    print("Non-zero pixels:")
    for ii, oi in samples:
        for i in range(ii.shape.h):
            for j in range(ii.shape.w):
                if ii[i, j] != 0:
                    print(f"({i}, {j}: {ii[i, j]})", end=" ")
        print("")

# print("What's the diff between the two images?")
# for ii, oi in samples:
#     for i in range(ii.shape.h):
#         for j in range(ii.shape.w):
#             if ii[i, j] != oi[i, j]:
#                 print(f"{i}, {j}: {ii[i, j]} -> {oi[i, j]}")
#     print("")

print("What's the same between the two images? (pixel movement)")
# iterative graph match ?
# 分类：对于每个像素，要么保持不变，要么移动到另一个位置，要么消失，要么产生，要么转变颜色。
# 不变：0， 移动：1， 消失：2， 产生：3， 转变颜色：4
for ii, oi in samples:
    s = ii.copy()
    for i in range(s.shape.h):
        for j in range(s.shape.w):
            if ii[i, j] == oi[i, j]:
                s[i, j] = 0
            elif ii[i, j] == 0:
                print(f"{i}, {j}: generated {oi[i, j]}")    # if move or copy. from where?
                s[i, j] = 3
            elif oi[i, j] == 0:
                print(f"{i}, {j}: disappeared {ii[i, j]}")
                s[i, j] = 2
            else:
                print(f"{i}, {j}: transformed {ii[i, j]} -> {oi[i, j]}")
                s[i, j] = 4
    print("")


plt.figure(f"{fn.rstrip('.json')}")
for si in range(ns):
    img_input = samples[si][0]
    img_output = samples[si][1]
    img_input.plot(plt.subplot(ns,2,si*2+1), f"Input")
    img_output.plot(plt.subplot(ns,2,si*2+2), f"Output")
plt.tight_layout()
plt.show()

# 学会基础概念，能够把握信息，信息量、信息源等概念。
