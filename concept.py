from typing import List
import numpy as np
from data import Image, Sample
from decision_tree import Node
# object is a set of positions.


class ColorMap:
    """find correct color map logic."""
    def __init__(self, node):
        self.node: Node = node
        # self.patterns = patterns
    def old_predict(self, inputs):
        if inputs in self.patterns:
            return self.patterns[inputs]
        else:
            for pattern, color in self.patterns.items():
                diff = 0
                for x, y in zip(inputs, pattern):
                    if x != y and y != 0:
                        diff += 1
                if diff == 0:
                    return color
            return 0
    def predict(self, inputs):
        return self.node.predict(inputs)
    def __call__(self, img: Image):
        def get_inputs(i, j):
            inputs = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    inputs.append(img[i+x, j+y])
            return tuple(inputs)
        def f(i, j):
            inputs = get_inputs(i, j)
            return self.predict(inputs)
        return Image.generate(f, img.shape)
    @staticmethod
    def get_all_patterns(samples: List[Sample]):
        patterns = {}
        for s in samples:
            input = s.input
            output = s.output
            if input.shape != output.shape:
                return None
            if input.shape[0] <= 3 or input.shape[1] <= 3:
                return None
            h, w = input.shape
            for i in range(h):
                for j in range(w):
                    inputs = []
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            inputs.append(input[i+x, j+y])
                    inputs = tuple(inputs)
                    if inputs not in patterns:
                        patterns[inputs] = output[i, j]
                    else:
                        if patterns[inputs] != output[i, j]:
                            return None
        # return patterns
        patterns = list(patterns.items())
        patterns_np = np.array([list(i) + [o] for i, o in patterns])
        node = Node(patterns_np[:, :-1], patterns_np[:, -1])
        if node.split() is None:
            return None
        # print(node)
        return ColorMap(node)

class PositionMap:  # include Resize, Rotate, Mirror, Translate
    """find correct position map logic, better in rigid transform."""
    def __init__(self, axis):
        assert axis in [0, 1], axis
        self.axis = axis

    def __call__(self, img: Image):
        h, w = img.shape
        f = lambda i, j: img[h-i-1, j] if self.axis == 0 else img[i, w-j-1]
        return Image.generate(f, img.shape)

