# Author: Dinger
# Data: 2024-08-08

import re
from time import time
import colorama
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Pattern:
    s: str
    update: int
    idxs: List[Tuple[int, int]]
    def key(self) -> int:
        return len(self.idxs)
    def __eq__(self, value):
        return self.key() == value.key()
    def __lt__(self, other):
        return self.key() < other.key()
    def __gt__(self, other):
        return self.key() > other.key()

def find_components(ss: List[str]) -> List[Dict[str, List[Tuple[int, int]]]]:
    last_cs = defaultdict(list)
    for idx_s, s in enumerate(ss):
        for idx_c, c in enumerate(s):
            last_cs[c].append((idx_s, idx_c))
    result = []
    while True:
        result.append(last_cs)
        new_cs = defaultdict(list)
        for c, idxs in last_cs.items():
            l = len(c)
            cs = defaultdict(list)
            for idx_s, idx_c in idxs:
                if idx_c + l >= len(ss[idx_s]):
                    continue
                cs[ss[idx_s][idx_c:idx_c+l+1]].append((idx_s, idx_c))
            for k,v in cs.items():
                if len(v) <= 1:
                    continue
                if len(set(i for i,_ in v)) == 1:
                    idx_cs = [j for _,j in v]
                    if max(idx_cs) - min(idx_cs) < l + 1:
                        continue
                new_cs[k].extend(v)
        if new_cs:
            last_cs = new_cs
        else:
            break
    return result

def find_components_with_c(ss: List[str], luts: List[Dict[int, List[int]]], p: Pattern) -> List[Tuple[int, int]]:
    if p.update >= len(luts):
        assert p.update == len(luts)
        return p.idxs
    cp = re.compile(p.s)
    new_idxs = []
    grouped_idxs = defaultdict(list)
    for idx_s, idx_c in p.idxs:
        grouped_idxs[idx_s].append(idx_c)
    for idx_s, idx_cs in grouped_idxs.items():
        need_update = False
        for l in range(p.update, len(luts)):
            if idx_s in luts[l]:
                need_update = True
                break
        if need_update:
            idx_ss = {idx_s}
            for l in range(p.update, len(luts)):
                next_idx_ss = set()
                for i in idx_ss:
                    if i in luts[l]:
                        next_idx_ss.update(luts[l][i])
                    else:
                        next_idx_ss.add(i)
                idx_ss = next_idx_ss
            for i in idx_ss:
                for it in cp.finditer(ss[i]):
                    new_idxs.append((i, it.start()))
        else:
            for idx_c in idx_cs:
                new_idxs.append((idx_s, idx_c))
    if len(new_idxs) <= 1:
        return None
    if len(set(i for i,_ in new_idxs)) == 1:
        idx_cs = [j for _,j in new_idxs]
        if max(idx_cs) - min(idx_cs) < len(p.s):
            return None
    # print(f"update {p.s} in {ss} with {luts} from {p.idxs} to {new_idxs}")
    return new_idxs

def find_ladderpath_of_level0(ss: List[str]) -> int:
    # base_components = defaultdict(int)
    # for s in ss:
    #     for c in s:
    #         base_components[c] += 1
    # for c, n in base_components.items():
    #     components.append((c, n))
    return sum(len(s) for s in ss)

def find_ladderpath_with_cs(ss: List[str], p: Pattern) -> Tuple[List[str], Dict[int, List[int]], int]:
    # print(f"replace {p.s} in {ss} with {p.idxs}")
    m_idx_cs = defaultdict(list)
    for idx_s, idx_c in p.idxs:
        m_idx_cs[idx_s].append(idx_c)
    replaced_cnt = 0
    lut = {}
    for idx_s, idx_cs in m_idx_cs.items():
        s = ss[idx_s]
        new_s = []
        lut[idx_s] = []
        last_i = 0
        for i in sorted(idx_cs):
            assert i + len(p.s) <= len(s)
            assert s[i:i+len(p.s)] == p.s
            if i < last_i:
                continue
            if i > last_i:
                new_s.append(s[last_i:i])
            replaced_cnt += 1
            last_i = i + len(p.s)
        if last_i < len(s):
            new_s.append(s[last_i:])
        if not new_s:
            ss[idx_s] = ""
        else:
            ss[idx_s] = new_s[0]
            lut[idx_s].append(idx_s)
        ss.extend(new_s[1:])
        lut[idx_s].extend(list(range(len(ss) - len(new_s) + 1, len(ss))))
    ss.append(p.s)
    c_pos = len(ss) - 1
    for idx_s in m_idx_cs:
        lut[idx_s].append(c_pos)
    # print(f"got {ss} with {lut}")
    assert replaced_cnt > 1
    # components.append((c, replaced_cnt - 1))
    return ss, lut, replaced_cnt - 1

def find_ladderpath(ss: List[str]) -> int:
    str_lens = [len(s) for s in ss]
    total_str_len = sum(str_lens)
    print(f'{len(ss)} strings, max_str_len: {max(str_lens)}, total_str_len: {total_str_len}')
    total_start_time = time()

    lp = 0
    luts = []
    component_start_time = time()
    css = find_components(ss)
    component_end_time = time()
    need_recompute = False
    level = len(css) - 1
    always_recompute = False
    print(f'Start from {level} level, components time: {component_end_time - component_start_time}s')
    while level > 0:
        if len(css[level]) >= 1000:
            always_recompute = True
        if need_recompute or always_recompute:
            luts = []
            component_start_time = time()
            last_duration = component_start_time - component_end_time
            css = find_components(ss)
            component_end_time = time()
            print(f'after {last_duration}s, Recompute components using {component_end_time - component_start_time}s')
            need_recompute = False
            assert len(css) - 1 <= level
            level = len(css) - 1
        cs = [Pattern(c, 0, idxs) for c, idxs in css[level].items()]
        cs = sorted(cs, key=lambda x: x.key(), reverse=True)
        level_component_cnt = 0
        process_start_time = time()
        while cs:
            max_cs = None
            updated_cs: List[Pattern] = []
            left_cs = cs[:]
            while max_cs is None or max_cs < left_cs[0]:
                idxs = find_components_with_c(ss, luts, left_cs[0])
                if idxs is not None:
                    new_c = Pattern(left_cs[0].s, len(luts), idxs)
                    updated_cs.append(new_c)
                    if max_cs is None or len(idxs) > len(max_cs.idxs):
                        max_cs = new_c
                left_cs = left_cs[1:]
                if len(left_cs) == 0:
                    break
            if len(cs) > 20 and len(updated_cs) + len(left_cs) < len(cs) // 2:
                need_recompute = True
            cs = sorted(updated_cs + left_cs, key=lambda x: x.key(), reverse=True)
            if max_cs is None:
                break
            assert max_cs.s == cs[0].s
            level_component_cnt += 1
            if level_component_cnt % 1000 == 0:
                now_time = time()
                print(f'processing {level} level, {len(ss)} strings, {level_component_cnt} components using {now_time - process_start_time}s')
                process_start_time = now_time
            ss, lut, new_lp = find_ladderpath_with_cs(ss, max_cs)
            lp += new_lp
            luts.append(lut)
            cs = cs[1:]
        if level_component_cnt > 0:
            print(f'processed {level} level, {len(ss)} strings, {level_component_cnt} components')
        level -= 1
    lp += find_ladderpath_of_level0(ss)
    duration = time() - total_start_time
    print(f'LP: {lp}, order: {total_str_len - lp}, size: {total_str_len}, total time: {duration}s')
    return lp

def compute_lp_graph(components):
    levels = [[]]
    for c, n in reversed(components):
        level = -1
        for l, cs in enumerate(levels):
            for b, bn in cs:
                c: str
                if c.find(b) >= 0:
                    level = l
                    break
            if level >= 0:
                break
        if level < 0:
            levels[-1].append((c, n))
        elif level == 0:
            levels = [[(c, n)]] + levels
        else:
            levels[level-1].append((c, n))
    levels_str = ' // '.join(', '.join(c if n == 1 else f'{c}({n})' for c, n in sorted(cs)) for cs in reversed(levels))
    print('{', levels_str, '}')

def test_sample():
    test_s = 'acsccsaascascaaaacssscscscasasacssacssaaaacsccsaascascaaaacssscscscasasacssacssaaa'
    test_lp = find_ladderpath([test_s])
    assert test_lp == 25, f'Test LP should be 25, but got {test_lp}'
    print("Test passed")

def compute_specie_lp():
    import pandas as pd

    data = pd.read_csv('../six_species.txt', sep='\t')
    # print([f'{s}: {len(data[data["Species"] == s])}' for s in set(data['Species'])])
    # MOUSE: 17119, CAEEL: 4381, ARATH: 16215, HUMAN: 20386, ECOLI: 4529, YEAST: 6727

    specie = 'ECOLI'
    specie_data = data[data['Species'] == specie]
    specie_strs = specie_data['Sequence'].tolist()
    
    find_ladderpath(specie_strs)

test_sample()
# compute_specie_lp()
