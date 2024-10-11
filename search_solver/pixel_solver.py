import os
import json

from dsl import *
from datatypes import *

# 通过像素构建基础关系
# 通过关系构建对象、在对象基础上构建更多关系。
# 如何由像素集合定义对象：通过某种关系的连通集。
# 对象拥有属性。像素组成的对象有颜色、形状、位置、大小等属性。
# 形状即忽略颜色、位置、大小等属性的对象。
# 颜色即忽略形状、位置、大小等属性的对象。
# 位置需要定义形状上的参考点来描述。
# 大小即忽略形状、颜色、位置等属性的对象。
# 不需要矩形等概念。矩形即同样长度的行的集合、或同样宽度的列的集合。
# 对称、重复等规律。


class Solver:
    def __init__(self, train_data):
        self.samples: List[Tuple[Image, Image]] = []
        self.working_outputs: List[Image] = []

        for sample in train_data:
            img_input = Image(sample['input'])
            img_output = Image(sample['output'])
            self.samples.append((img_input, img_output))
            polymers_input = aggregation2d(img_input, neighbor_with_same_color)
            polymers_output = aggregation2d(img_output, neighbor_with_same_color)
            img_input.polymers = polymers_input
            img_output.polymers = polymers_output
    def what_we_need_now(self):
        if not self.working_outputs:
            def construct_output(shape_rule):
                print(f"Constructing black output image use {shape_rule}")
                for si, sample in enumerate(self.samples):
                    shape = use_sample(shape_rule, sample).get_value()
                    image = [[0 for _ in range(shape.w)] for _ in range(shape.h)]
                    self.working_outputs.append(Image(image))
            return PApply(FShape(), POutput(PAnySample())), construct_output
        return None, None
    def check_special(self, values, picked_idxs):
        for sample, idxs in zip(self.samples, picked_idxs):
            xs = use_sample(values, sample).get_value()
            if len(idxs) != 1:  # 假设只选择了一个值
                return False
            i = idxs[0]
            if not all(x != xs[i] for ii, x in enumerate(xs) if ii != i):
                return False
        return True
    def find_special(self, values, pick_func):
        picked_idxs = []
        for si, sample in enumerate(self.samples):
            xs = use_sample(values, sample).get_value()
            picked_idx = []
            for i, x in enumerate(xs):
                if pick_func(x, si):
                    picked_idx.append(i)
            picked_idxs.append(picked_idx)
        if self.check_special(PMap(values, FColor()), picked_idxs):
            print(f"Seems it's from a special colored {values}")
            picked_values = []
            for sample, idxs in zip(self.samples, picked_idxs):
                xs = use_sample(PMap(values, FColor()), sample).get_value()
                picked_values.append(PConstant(xs[idxs[0]]))
            color_rule = self.find_rule(picked_values)
            if color_rule:
                return PPick(values, FCompose(FEqual(color_rule), FColor()))
        # Cannot find special for this value
    def check_rule(self, need_values, expect):
        for need_value, sample in zip(need_values, self.samples):
            if need_value != use_sample(expect, sample).get_value():
                return False
        return True
    def find_rule(self, need):
        # 寻找所需量的来源，确保一致性和唯一特殊性
        if isinstance(need, Pointer):
            print(f"Try to find the rule of the {need}.")
            # 假设need含有PAnySample()
            need_values = []
            for si in range(len(self.samples)):
                need_values.append(use_sample(need, self.samples[si]).get_value())
            need_type = need.return_type
        else: # List[Pointer]
            assert len(need) == len(self.samples)
            need_values = [n.get_value() for n in need]
            assert all(type(n) == type(need[0]) for n in need)
            need_type = need[0].return_type
            print(f"Try to find the rule of {need}.")

        expect = PConstant(need_values[0])
        if self.check_rule(need_values, expect):
            print(f"Seems it's from a Constant of {expect}")
            return expect
        if need_type == Shape:
            expect = PApply(FShape(), PInput(PAnySample()))
            if self.check_rule(need_values, expect):
                return expect
            expect_polymer = self.find_special(PPolymers(PInput(PAnySample())),
                                    lambda p, si: p.shape == need_values[si])
            if expect_polymer:
                return PApply(FShape(), expect_polymer)
        # Cannot find rule for this need.
    def get_solver(self):
        # 为所有训练和测试输入逐步构造输出
        now_need, op = self.what_we_need_now()
        while now_need:
            rule = self.find_rule(now_need)
            if rule:
                op(rule)
            else:
                print(f"Cannot find the rule.")
                break
            now_need, op = self.what_we_need_now()


def test_ladderpath():
    path = '../../ARC-AGI/data/training'
    for fn in os.listdir(path):
        with open(f'{path}/{fn}') as f:
            data = json.load(f)
            print(f"\nSolving {fn.rstrip('.json')}")
            solver = Solver(data['train'])
            solver.get_solver()
            ns = len(data['train'])
            plt.figure(f"{fn.rstrip('.json')}")
            for si in range(ns):
                img_input = solver.samples[si][0]
                img_output = solver.samples[si][1]
                img_input.plot(plt.subplot(ns,2,si*2+1), f"Input")
                img_output.plot(plt.subplot(ns,2,si*2+2), f"Output")
            plt.tight_layout()
            plt.show()


if __name__ == '__main__':
    test_ladderpath()
