import os
import json
from math import floor

from datatypes import *
from dsl import *


def calc_ladderpath(img: Image) -> int:
    bg = PureImage.find_pure_image(img)
    img = PureImage.remove_background(img, bg)
    lp = 1  # for bg
    rect = DrawRect.find_rect(img)
    while rect is not None:
        img = DrawRect.remove_rect(img, rect)
        rect = DrawRect.find_rect(img)
        lp += 1
    return lp


def test_ladderpath():
    path = '../../ARC-AGI/data/training'
    total_size = 0
    total_lp = 0
    for fn in os.listdir(path):
        with open(f'{path}/{fn}') as f:
            data = json.load(f)
            for si, sample in enumerate(data['train']):
                img_input = Image(sample['input'])
                img_output = Image(sample['output'])
                total_size += img_input.height * img_input.width + img_output.height * img_output.width
                lp_input = calc_ladderpath(img_input)
                lp_output = calc_ladderpath(img_output)
                total_lp += lp_input + lp_output
                plt.figure(f"{fn.rstrip('.json')}[{si}]")
                img_input.plot(plt.subplot(1,2,1), f"Input - {lp_input}")
                img_output.plot(plt.subplot(1,2,2), f"Output - {lp_output}")
                plt.tight_layout()
                plt.show()
                break
    print(f'Total size: {total_size}')
    print(f'Total ladderpath: {total_lp}')


def test_dsl():
    path = '../../ARC-AGI/data/training'
    # fn = 'ba26e723.json'
    fn = '09629e4f.json'
    with open(f'{path}/{fn}') as f:
        data = json.load(f)
        sample = data['train'][0]
        img = Image(sample['output'])
        img.plot(plt.subplot(1,1,1), f"{0}")
        plt.tight_layout()
        plt.show()
        bg = PureImage.find_pure_image(img)
        img = PureImage.remove_background(img, bg)
        img.plot(plt.subplot(1,1,1), f"{1}")
        plt.tight_layout()
        plt.show()
        lp = 1  # for bg
        rect = DrawRect.find_rect(img)
        while rect is not None:
            img = DrawRect.remove_rect(img, rect)
            img.plot(plt.subplot(1,1,1), f"{lp+1}")
            plt.tight_layout()
            plt.show()
            rect = DrawRect.find_rect(img)
            lp += 1


def test_relation(fn):
    path = '../../ARC-AGI/data/training'
    with open(f'{path}/{fn}') as f:
        data = json.load(f)
    sample = data['train'][0]
    img = Image(sample['output'])
    fig, (ax1, ax2) = plt.subplots(1, 2)
    img.plot(ax1, f"{0}")
    fig.tight_layout()

    polymers = aggregation2d(img, neighbor_with_same_color)

    def f(i, j):
        # 同行、同列、同色、（某种）相邻、（某种）连通
        c = img[i, j]
        for p in polymers:
            if Position(i, j) in p.pixels:
                polymer = p
                break
        img_b = Image([[0 for j in range(img.width)] for i in range(img.height)])
        for p in polymer.pixels:
            img_b[p.i, p.j] = 1
        # for k in range(img.height):
        #     for l in range(img.width):
        #         cnt = 0
        #         # if i == k: cnt += 1
        #         # if j == l: cnt += 1
        #         # if c == img[k, l]: cnt += 1
        #         # if (k, l) in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]: cnt += 1
        #         img_b[k, l] = cnt
        return img_b

    def onclick(event):
        if event.inaxes == ax1:
            i, j = floor(event.ydata+0.5), floor(event.xdata+0.5)
            f(i, j).plot(ax2, f"{i},{j}")
            fig.canvas.draw()
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()


if __name__ == '__main__':
    path = '../../ARC-AGI/data/training'
    for fn in os.listdir(path):
        test_relation(fn)
    # test_ladderpath()
    # test_dsl()
