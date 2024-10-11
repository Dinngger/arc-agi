import os
import json

from datatypes import *
from dsl import *


def calc_ladderpath(img: Image) -> List[DrawRect]:
    rects = []
    rect = PureImage.find_pure_image(img)
    while rect is not None:
        rects.append(rect)
        img = DrawRect.remove_rect(img, rect)
        rect = DrawRect.find_rect(img)
    return rects


class Solver:
    def __init__(self, train_data):
        self.samples: List[Tuple[Image, Image]] = []
        self.rects: List[Tuple[List[DrawRect], List[DrawRect]]] = []
        for sample in train_data:
            img_input = Image(sample['input'])
            img_output = Image(sample['output'])
            self.samples.append((img_input, img_output))
            lp_input = calc_ladderpath(img_input)
            lp_output = calc_ladderpath(img_output)
            self.rects.append((lp_input, lp_output))
    @staticmethod
    def all_same(xs) -> bool:
        return all(x == xs[0] for x in xs)
    @staticmethod
    def is_special(xs, i) -> bool:
        return all(x != xs[i] for xi, x in enumerate(xs) if xi != i)
    @staticmethod
    def update_same_value(old, new):
        if old is not None and old != new:
            raise ValueError(f"Cannot update {old} to {new}")
        return new
    def is_special_color(self, ids: List[int]) -> Optional[Color]:
        colors = [rects[i].color for (rects, _), i in zip(self.rects, ids)]
        if not self.all_same(colors):
            return None
        if all(self.is_special([r.color for r in rects[0]], i)
               for rects, i in zip(self.rects, ids)):
            return colors[0]
        return None
    def get_shapes(self, shapes):
        special_color = None
        for shape, rects in zip(shapes, self.rects):
            same_shapes = [i for i, r in enumerate(rects[0]) if r.shape == shape]
            assert len(same_shapes) == 1
            assert self.is_special([r.color for r in rects[0]], same_shapes[0])
            c = rects[0][same_shapes[0]].color
            special_color = self.update_same_value(special_color, c)
        return special_color
    def find_direct_relations(self):
        direct_relations = [[] for _ in self.rects]
        self.relation_mat = []
        for si, (rects_input, rects_output) in enumerate(self.rects):
            relation_mat = np.zeros((len(rects_input), len(rects_output)))
            for oi, ro in enumerate(rects_output):
                for ii, ri in enumerate(rects_input):
                    if ri.color == ro.color:
                        direct_relations[si].append((ii, oi, 'same_color'))
                        relation_mat[ii, oi] += 1
                    if ri.shape.h == ro.shape.h:
                        direct_relations[si].append((ii, oi,'same_height'))
                        relation_mat[ii, oi] += 1
                    if ri.shape.w == ro.shape.w:
                        direct_relations[si].append((ii, oi,'same_width'))
                        relation_mat[ii, oi] += 1
                    if ri.pos.i == ro.pos.i:
                        direct_relations[si].append((ii, oi, 'same_row'))
                        relation_mat[ii, oi] += 1
                    if ri.pos.j == ro.pos.j:
                        direct_relations[si].append((ii, oi, 'same_col'))
                        relation_mat[ii, oi] += 1
            self.relation_mat.append(relation_mat)
    def find_common_relations(self):
        pass
    def get_solver(self):
        self.find_direct_relations()
        # print(f"Direct relations: {self.direct_relations}")
        # out_shape = self.get_shapes([s[1].shape for s in self.samples])
        # print(f"Special color: {out_shape}")


def test_ladderpath():
    path = '../../ARC-AGI/data/training'
    for fn in os.listdir(path):
        with open(f'{path}/{fn}') as f:
            data = json.load(f)
            solver = Solver(data['train'])
            solver.get_solver()
            ns = len(data['train'])
            plt.figure(f"{fn.rstrip('.json')}")
            for si in range(ns):
                img_input = solver.samples[si][0]
                img_output = solver.samples[si][1]
                img_input.plot(plt.subplot(ns,3,si*3+1), f"Input - {len(solver.rects[si][0])}")
                img_output.plot(plt.subplot(ns,3,si*3+2), f"Output - {len(solver.rects[si][1])}")
                plt.subplot(ns,3,si*3+3).imshow(solver.relation_mat[si])
            plt.tight_layout()
            plt.show()


if __name__ == '__main__':
    test_ladderpath()
