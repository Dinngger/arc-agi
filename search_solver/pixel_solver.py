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

# 所有方法，自然而优雅，看似复杂，但也很自然很简单。
# 核心矛盾：图像中的信息很显然并且容易获取，但仅仅是模糊的信息。但是求解器空间是人为定义的，明确的，有限的。
# 当前定义的求解器空间并未覆盖所有可能！！


class Solver:
    def __init__(self, train_data):
        self.samples: List[Tuple[Image, Image]] = []
        self.working_outputs: List[Image] = []
        for sample in train_data:
            img_input = Image(sample['input'])
            img_output = Image(sample['output'])
            self.samples.append((img_input, img_output))
        self.preanalysis()
    def preanalysis(self):
        for img_input, img_output in self.samples:
            # 通过函数定义polymer的来源，以此做特殊性区分和求解过程记录。
            for relation in [FNeighbors(), FNeighbors(col=False), FNeighbors(raw=False), FNeighbors(diag=True)]:
                img_input.polymers[relation] = aggregation2d(img_input, relation)
                img_output.polymers[relation] = aggregation2d(img_output, relation)
            # 聚合仅仅只是一种局部视角，还需要一种全局视角。
            # 全局区域划分方法：通过模糊分割、模糊聚合、及这二者的结合，识别对象。
            img_input.polymers[FCanCat('inner', FNeighbors(diag=True))] = \
                aggregation(img_input, img_input.polymers[FNeighbors(diag=True)], FCanCat('inner', FNeighbors(diag=True)))
            img_input.polymers[FCanCat('image', FNeighbors(diag=True))] = \
                aggregate_to_image(img_input, img_input.polymers[FNeighbors(diag=True)])
            img_input.polymers[FCanCat('split', FNeighbors())] = \
                split_polymers(img_input, img_input.polymers[FNeighbors()])
    def what_we_need_now(self):
        if not self.working_outputs:
            def construct_output(shape_rule: Function):
                print(f"Constructing black output image use {shape_rule}")
                for si, sample in enumerate(self.samples):
                    shape = shape_rule.call(sample)
                    image = [[0 for _ in range(shape.w)] for _ in range(shape.h)]
                    self.working_outputs.append(Image(image))
            return FCompose(FShape(), FOutput()), construct_output
        return None, None
    def check_sufficient(self, values: Function, picked_idxs):
        for sample, idxs in zip(self.samples, picked_idxs):
            xs = values.call(sample)
            picked_values = [xs[i] for i in idxs]
            if not all(x == picked_values[0] for x in picked_values):
                print(f"Not all picked values are the same, they are {picked_values}")
                return False
        return True
    def check_necessary(self, values: Function, picked_idxs):
        for sample, idxs in zip(self.samples, picked_idxs):
            xs = values.call(sample)
            picked_values = [xs[i] for i in idxs]
            unpicked_values = [x for i, x in enumerate(xs) if i not in idxs]
            necessary = False
            for x in picked_values:
                if x not in unpicked_values:
                    necessary = True
                    break
            if not necessary:
                print(f"None of the picked values are necessary")
                return False
        return True
    def check_necessary_value(self, values: list, picked_idxs):
        for xs, idxs in zip(values, picked_idxs):
            picked_values = [xs[i] for i in idxs]
            unpicked_values = [x for i, x in enumerate(xs) if i not in idxs]
            necessary = False
            for x in picked_values:
                if x not in unpicked_values:
                    necessary = True
                    break
            if not necessary:
                print(f"None of the picked values are necessary")
                return False
        return True
    def is_constant(self, values):
        if all(x == values[0] for x in values):
            return True
        return False
    def find_count_special(self, colors, picked_idxs):
        print(f"try to find the pick rule of count for colors {colors}")
        picked_colors = [[cs[i] for i in idxs] for cs, idxs in zip(colors, picked_idxs)]
        for cs in picked_colors:
            if not self.is_constant(cs):
                print(f"Not all picked colors are the same, they are {cs}")
                return None
        counts = [Counter(cs) for cs in colors]
        most_nums = [c.most_common(1)[0][1] for c in counts]
        least_nums = [c.most_common()[-1][1] for c in counts]
        most_colors = [[color for color, num in c.items() if num == most_num] for c, most_num in zip(counts, most_nums)]
        least_colors = [[color for color, num in c.items() if num == least_num] for c, least_num in zip(counts, least_nums)]
        if all(picked_cs[0] in cs for cs, picked_cs in zip(most_colors, picked_colors)):
            if all(len(cs) == 1 for cs in most_colors):
                print(f"Seems it's the most common color.")
                return FMost(True)
            else:
                print(f"Seems it's one of the most common colors, but which one?")
                return FMost(False)
        if all(picked_cs[0] in cs for cs, picked_cs in zip(least_colors, picked_colors)):
            if all(len(cs) == 1 for cs in least_colors):
                print(f"Seems it's the least common color.")
                return FLeast(True)
            else:
                print(f"Seems it's one of the least common colors, but which one?")
                return FLeast(False)
    def pick_the_only_one(self, values, picked_idxs):
        if all(len(vs) == 1 for vs in values):
            print(f"Seems there are only one value to pick.")
            return FPick()
    def pick_one_from_two(self, values, picked_idxs):
        if not all(len(idxs) == 1 for idxs in picked_idxs):
            return None
        if not all(len(cs) == 2 for cs in values):
            return None
        unpicked_values = [xs[1 - idxs[0]] for xs, idxs in zip(values, picked_idxs)]
        if self.is_constant(unpicked_values):
            print(f"Seems it's picking one that is not equal to {unpicked_values[0]}.")
            context = Context([List[Color]])
            return FDefine(1, context, PPick(PArg(context, 0), FCompose(FNot(), Apply(FEqual(), PConstant(unpicked_values[0])))))
    def find_special_nominal_int(self, colors, picked_idxs):
        pick_rule = self.pick_the_only_one(colors, picked_idxs)
        if pick_rule:
            return pick_rule
        picked_values = [[cs[i] for i in idxs] for cs, idxs in zip(colors, picked_idxs)]
        if not all(isinstance(c, int) for cs in colors for c in cs):
            print(f"Not all colors are integers")
            print(f"pick {picked_values} from {colors}")
            return None
        if not all(self.is_constant(cs) for cs in picked_values):
            return None
        if self.is_constant([cs[0] for cs in picked_values]):
            print(f"Seems it's picking the color {picked_values[0][0]}")
            if self.check_necessary_value(colors, picked_idxs):
                context = Context([List[Color]])
                return FDefine(1, context, PPick(PArg(context, 0), Apply(FEqual(), PConstant(picked_values[0][0]))))
        count_rule = self.find_count_special(colors, picked_idxs)
        if count_rule is not None:
            if count_rule.strict:
                return count_rule
            else:
                colors = [count_rule.call(cs) for cs in colors]
                picked_idxs = [[i for i, c in enumerate(cs) if c == picked_cs[0]] for cs, picked_cs in zip(colors, picked_values)]
        pick_rule = self.pick_one_from_two(colors, picked_idxs)
        if pick_rule:
            if count_rule:
                return FCompose(pick_rule, count_rule)
            else:
                return pick_rule
    def find_special_scale_int(self, values, picked_idxs):
        pick_rule = self.pick_the_only_one(values, picked_idxs)
        if pick_rule:
            return pick_rule
        picked_values = [[vs[i] for i in idxs] for vs, idxs in zip(values, picked_idxs)]
        print(f"try to find the pick rule of scale int.")
        if not all(self.is_constant(cs) for cs in picked_values):
            return None
        if all(pvs[0] == max(vs) for vs, pvs in zip(values, picked_values)):
            print(f"Seems it's the largest value.")
            return FCompose(FFirst(), FSort(reverse=True))
        if all(pvs[0] == min(vs) for vs, pvs in zip(values, picked_values)):
            print(f"Seems it's the smallest value.")
            return FCompose(FFirst(), FSort())
    def find_special_polymer(self, values: Function, pick_func):
        """ find why the picked values are different from others. """
        picked_idxs = []
        for si, sample in enumerate(self.samples):
            xs = values.call(sample)
            picked_idx = []
            for i, x in enumerate(xs):
                if pick_func(x, si):
                    picked_idx.append(i)
            if not picked_idx:
                return None
            picked_idxs.append(picked_idx)
        pick_rule = self.pick_the_only_one([values.call(sample) for sample in self.samples], picked_idxs)
        if pick_rule:
            return FCompose(pick_rule, values)
        print(f"Picked some needed things for {values}, try to find the special rule.")
        context = Context([Tuple[Image, Image]])
        p_sample = PArg(context, 0)
        p_img = Apply(values.operands[1], p_sample)
        p_polymers = Apply(values, p_sample)
        f_size = FCompose(FMap(FCompose(FShapeSize(), FShape())), values)
        if self.check_sufficient(f_size, picked_idxs):
            print(f"Seems it's from a special size {values}")
            if not self.check_necessary(f_size, picked_idxs):
                print(f"But it's not necessary.")
                return None
            sizes = [f_size.call(sample) for sample in self.samples]
            size_pick_rule = self.find_special_scale_int(sizes, picked_idxs)
            if size_pick_rule:
                need_size = Apply(size_pick_rule, Apply(FMap(FCompose(FShapeSize(), FShape())), p_polymers))
                return FDefine(1, context, PPick(p_polymers, FCompose(Apply(FEqual(), need_size), FCompose(FShapeSize(), FShape()))))

        f_colors = FDefine(1, context, Apply(FMap(Apply(FColor(), p_img)), p_polymers))
        if self.check_sufficient(f_colors, picked_idxs):
            print(f"Seems it's from a special colored {values}")
            if not self.check_necessary(f_colors, picked_idxs):
                print(f"But it's not necessary.")
                return None
            colors = [f_colors.call(sample) for sample in self.samples]
            color_pick_rule = self.find_special_nominal_int(colors, picked_idxs)
            if color_pick_rule:
                p_colors = Apply(FMap(Apply(FColor(), p_img)), p_polymers)
                need_color = Apply(color_pick_rule, p_colors)
                return FDefine(1, context, PPick(p_polymers, FCompose(Apply(FEqual(), need_color), Apply(FColor(), p_img))))
            # color_rule = self.find_rule(picked_values)    # 这里需要在find_rule中排除当前颜色的来源，否则会陷入循环论证。
            # if color_rule:
            #     need_color = Apply(color_rule, p_sample)
            #     p_colors = Apply(FMap(Apply(FColor(), p_img)), p_polymers)
            #     return FDefine(1, context, PPick(p_polymers, Apply(Apply(FEqual(), need_color), p_colors)))
        # Cannot find special for this value
    def find_shape_scale(self, need_values, input_shapes):
        """find if the need_values is a scale of input_shapes, assume need_values is larger than input_shapes."""
        for ins, ns in zip(input_shapes, need_values):
            if ns.h % ins.h != 0 or ns.w % ins.w != 0:
                return None
        h_scales = [need_values[si].h // input_shapes[si].h for si in range(len(self.samples))]
        w_scales = [need_values[si].w // input_shapes[si].w for si in range(len(self.samples))]
        if not self.is_constant(h_scales) or not self.is_constant(w_scales):
            return None
        return FShapeScale(h_scales[0], w_scales[0])
    def find_shape_rule(self, need_values):
        input_shape_rule = FCompose(FShape(), FInput())
        input_shapes = [input_shape_rule.call(sample) for sample in self.samples]
        if all(ins == ns for ins, ns in zip(input_shapes, need_values)):
            return input_shape_rule
        scale_rule = self.find_shape_scale(need_values, input_shapes)
        if scale_rule:
            return FCompose(scale_rule, input_shape_rule)
        # 对于部分相似polymer，例如height一样，或者width一样，可以通过融合来形成需要的Image。
        expect_polymer = self.find_special_polymer(FCompose(FPolymers(FNeighbors(diag=True)), FInput()),
                                lambda p, si: FShapeScale(2, 2).call(p.shape) == need_values[si])
        if expect_polymer:
            return FCompose(FShapeScale(2, 2), FCompose(FShape(), expect_polymer))
        expect_polymer = self.find_special_polymer(FCompose(FPolymers(FCanCat('inner', FNeighbors(diag=True))), FInput()),
                                lambda p, si: p.shape == need_values[si])
        if expect_polymer:
            return FCompose(FShape(), expect_polymer)
        expect_polymer = self.find_special_polymer(FCompose(FPolymers(FCanCat('image', FNeighbors(diag=True))), FInput()),
                                lambda p, si: p.shape == need_values[si])
        if expect_polymer:
            return FCompose(FShape(), expect_polymer)
        expect_polymer = self.find_special_polymer(FCompose(FPolymers(FCanCat('split', FNeighbors())), FInput()),
                                lambda p, si: p.shape == need_values[si])
        if expect_polymer:
            return FCompose(FShape(), expect_polymer)
    def find_rule(self, need):
        # 寻找所需量的来源，确保一致性和唯一特殊性
        # 可以通过部分相似来构造来源，由于噪声、遮挡等原因造成形状不完全一致。
        if isinstance(need, Function):
            print(f"Try to find the rule of the {need} samples.")
            # 假设need含有PAnySample()
            need_values = []
            for si in range(len(self.samples)):
                need_values.append(need.call(self.samples[si]))
            need_type = need.return_type
        else: # List[Pointer]
            assert len(need) == len(self.samples)
            need_values = [n.call(s) for n, s in zip(need, self.samples)]
            assert all(n.return_type == need[0].return_type for n in need)
            need_type = need[0].return_type
            print(f"Try to find the rule of {need}.")

        if self.is_constant(need_values):
            print(f"Seems it's from a Constant of {need_values[0]}")
            return FConstant(need_values[0])
        if need_type == Shape:
            shape_rule = self.find_shape_rule(need_values)
            if shape_rule:
                return shape_rule
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
                return False
            now_need, op = self.what_we_need_now()
        return True


def test_ladderpath():
    path = '../../ARC-AGI/data/training'
    cnt = 0
    for fn in sorted(os.listdir(path)):
        with open(f'{path}/{fn}') as f:
            data = json.load(f)
            print(f"\nSolving {fn.rstrip('.json')}")
            solver = Solver(data['train'])
            if solver.get_solver():
                cnt += 1
            continue
            ns = len(data['train'])
            plt.figure(f"{fn.rstrip('.json')}")
            for si in range(ns):
                img_input = solver.samples[si][0]
                img_output = solver.samples[si][1]
                img_input.plot(plt.subplot(ns,2,si*2+1), f"Input")
                img_output.plot(plt.subplot(ns,2,si*2+2), f"Output")
            plt.tight_layout()
            plt.show()
            break
    print(f"Solved {cnt} tasks.")


if __name__ == '__main__':
    test_ladderpath()
