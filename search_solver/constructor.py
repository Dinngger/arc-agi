import os
import json

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


if __name__ == '__main__':
    test_ladderpath()
    # test_dsl()
