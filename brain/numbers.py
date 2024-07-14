from collections import defaultdict
from dataclasses import dataclass
from brain.image import Image

class Counter:
    def __init__(self, data):
        self.data = data
        self.count = defaultdict(int)
        for d in self.data:
            self.count[d] += 1
        self.most = max(self.count, key=self.count.get)
        self.least = min(self.count, key=self.count.get)
        self.min = min(self.data)
        self.max = max(self.data)

def img_color_counter(img: Image):
    return Counter([img[i, j] for i in range(img.height)
                              for j in range(img.width)])

@dataclass
class MostColor:
    def __call__(self, img: Image) -> int:
        counter = img_color_counter(img)
        return counter.most

def find_most_color(img: Image, color: int):
    counter = img_color_counter(img)
    if color == counter.most:
        return MostColor()
    else:
        return None

@dataclass
class ColorCount:
    def __call__(self, img: Image) -> int:
        counter = img_color_counter(img)
        counter.count.pop(0, None)
        return len(counter.count)
