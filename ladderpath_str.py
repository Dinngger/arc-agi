from collections import Counter

class Component:
    pass

base_components = {'a', 'b', 'c', 'd'}

class Operator:
    pass

class Concat(Operator):
    def __init__(self, xs):
        self.xs = xs
    def __len__(self):
        return len(self.xs)

class Ladderpath:
    def __init__(self, components):
        self.components = components
    def __len__(self):
        l = 1
        for s in self.components:
            for c in s:
                l += len(c) - 1
        return l

s = 'abcabdabc'
# { a, b, c, d // ab // abc // abcabdabc}
ab = Concat(['a', 'b'])
abc = Concat([ab, 'c'])
abcabdabc = Concat([abc, ab, 'd', abc])
ladderpath = Ladderpath([['a', 'b', 'c', 'd'], [ab], [abc], [abcabdabc]])
# ( Ladderpath-index:6,  Order-index:3,  Size-index:9 )
assert len(ladderpath) == 6


min_ladderpath = None
import os
def find_ladderpath(s: str, cnt=0, his=[]):
    global min_ladderpath
    # assert chr(cnt) not in s
    assert cnt < 10
    all_2_grams = [s[i:i+2] for i in range(len(s)-1)]
    count = Counter(all_2_grams)
    count = [k for k,v in count.items() if v > 1]
    if not count:
        if min_ladderpath > len(s) + cnt:
            print(f'find {len(s) + cnt} length ladderpath')
            print(f'cnt = {cnt}, s = {s}, his = {his}')
            if len(s) + cnt == 24:
                os._exit(0)
        min_ladderpath = min(min_ladderpath, len(s) + cnt)
        # print(f'find {len(s) + cnt} length ladderpath {s}')
        # if min_ladderpath is None:
        #     min_ladderpath = len(s) + cnt
        # else:
        #     assert min_ladderpath <= len(s) + cnt
    for k in count:
        # new_s = s.replace(k, str(chr(cnt)))
        new_s = s.replace(k, str(cnt))
        # print(f"replacing {k} with {cnt} in {s} gives {new_s}")
        find_ladderpath(new_s, cnt+1, his+[k])

from sys import argv
min_ladderpath = len(argv[1])
find_ladderpath(argv[1])
print(min_ladderpath)

# acsccsaascascaaaacssscscscasasacssacssaaa
# 0:ac 1:0s 2:aa 3:as 4:sc 5:43 6:2a 7:1s
# 1ccs25c674453776
# { a, c, s // 0, 2, 3, 4 // 1, 5, 6 // 7}
# { a, c, s // ac, aa, as, sc // acs, scas, aaa // acss}
