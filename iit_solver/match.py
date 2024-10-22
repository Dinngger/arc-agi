# What's the same between the two images? (pixel movement)
# iterative graph match ?
# 分类：对于每个像素，要么保持不变，要么移动到另一个位置，要么消失，要么产生，要么转变颜色。
# 不变：0， 移动：1， 消失：2， 产生：3， 转变颜色：4

import os
import json
import random
from datatypes import *


class PixelState:
    def __init__(self, sample: Tuple[Image, Image]):
        self.input_img, self.output_img = sample
        self.pixel_state = self.input_img.copy()
        for i in range(self.pixel_state.shape.h):
            for j in range(self.pixel_state.shape.w):
                if self.input_img[i, j] == self.output_img[i, j]:
                    self.pixel_state[i, j] = 0
                elif self.input_img[i, j] == 0:
                    self.pixel_state[i, j] = 3
                elif self.output_img[i, j] == 0:
                    self.pixel_state[i, j] = 2
                else:
                    self.pixel_state[i, j] = 4


if __name__ == '__main__':
    path = '../../ARC-AGI/data/training'
    files = os.listdir(path)
    random.shuffle(files)
    for fn in files:
        with open(f'{path}/{fn}') as f:
            data = json.load(f)
            ns = len(data['train'])
            samples: List[Tuple[Image, Image]] = []
            for sample in data['train']:
                img_input = Image(sample['input'])
                img_output = Image(sample['output'])
                samples.append((img_input, img_output))
            if not all(img_input.shape == img_output.shape for img_input, img_output in samples):
                continue
            states: List[Image] = []
            for sample in samples:
                states.append(PixelState(sample).pixel_state)
            print(f"Solving {fn.rstrip('.json')}")
            plt.figure(f"{fn.rstrip('.json')}")
            for si in range(ns):
                img_input = samples[si][0]
                img_output = samples[si][1]
                img_input.plot(plt.subplot(ns,3,si*3+1), f"Input")
                img_output.plot(plt.subplot(ns,3,si*3+2), f"Output")
                states[si].plot(plt.subplot(ns,3,si*3+3), f"State")
            plt.tight_layout()
            plt.show()
            break
