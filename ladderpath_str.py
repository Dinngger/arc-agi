# Author: Dinger
# Data: 2024-08-14

import re
import json
from time import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple

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

ID_t = int
class Ladderon:
    def __init__(self, id, s):
        self.ID: ID_t = id
        self.STR: str = s
        self.POS: Dict[ID_t, List[int]] = defaultdict(list)
        self.COMP: Set[ID_t] = set()
    def make_ref(self) -> 'LadderonRef':
        return LadderonRef(self, 0, len(self.STR), self.STR)
    def asdict(self) -> dict:
        return {"ID": self.ID, "STR": self.STR, "POS": self.POS, "COMP": list(self.COMP)}
    def __repr__(self):
        return json.dumps(self.asdict())

@dataclass
class LadderonRef:
    ladderon: Ladderon
    start: int
    end: int
    s: str
    def slice(self, start, end) -> 'LadderonRef':
        return LadderonRef(self.ladderon, self.start + start, self.start + end, self.s[start:end])

def find_components(ss: List[LadderonRef]) -> List[Dict[str, List[Tuple[int, int]]]]:
    last_cs = defaultdict(list)
    for idx_s, s in enumerate(ss):
        if s is None:
            continue
        for idx_c, c in enumerate(s.s):
            last_cs[c].append((idx_s, idx_c))
    result = []
    while True:
        result.append(last_cs)
        new_cs = defaultdict(list)
        for c, idxs in last_cs.items():
            l = len(c)
            cs = defaultdict(list)
            for idx_s, idx_c in idxs:
                if idx_c + l >= len(ss[idx_s].s):
                    continue
                cs[ss[idx_s].s[idx_c:idx_c+l+1]].append((idx_s, idx_c))
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

def find_components_with_c(ss: List[LadderonRef], luts: List[Dict[int, List[int]]], p: Pattern) -> List[Tuple[int, int]]:
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
                for it in cp.finditer(ss[i].s):
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

def find_ladderpath_of_level0(ss: List[LadderonRef], components: List[Ladderon]) -> int:
    base_components: Dict[str, Ladderon] = {}
    for s in ss:
        if s is None: continue
        for i, c in enumerate(s.s):
            if c not in base_components:
                base_components[c] = Ladderon(len(components), c)
                components.append(base_components[c])
            base_components[c].POS[s.ladderon.ID].append(i)
            s.ladderon.COMP.add(base_components[c].ID)
    return sum(0 if s is None else len(s.s) for s in ss)

def find_ladderpath_with_cs(ss: List[LadderonRef], p: Pattern, components: List[Ladderon]) -> Tuple[List[LadderonRef], Dict[int, List[int]], int]:
    # print(f"replace {p.s} in {ss} with {p.idxs}")
    m_idx_cs = defaultdict(list)
    for idx_s, idx_c in p.idxs:
        m_idx_cs[idx_s].append(idx_c)
    replaced_cnt = 0
    lut = {}
    new_ladderon = Ladderon(len(components), p.s)
    for idx_s, idx_cs in m_idx_cs.items():
        s: LadderonRef = ss[idx_s]
        s.ladderon.COMP.add(new_ladderon.ID)
        new_s: List[LadderonRef] = []
        lut[idx_s] = []
        last_i = 0
        for i in sorted(idx_cs):
            assert i + len(p.s) <= len(s.s)
            assert s.s[i:i+len(p.s)] == p.s
            if i < last_i:
                continue
            if i > last_i:
                new_s.append(s.slice(last_i, i))
            replaced_cnt += 1
            new_ladderon.POS[s.ladderon.ID].append(i)
            last_i = i + len(p.s)
        if last_i < len(s.s):
            new_s.append(s.slice(last_i, len(s.s)))
        if not new_s:
            ss[idx_s] = None
        else:
            ss[idx_s] = new_s[0]
            lut[idx_s].append(idx_s)
        ss.extend(new_s[1:])
        lut[idx_s].extend(list(range(len(ss) - len(new_s) + 1, len(ss))))
    ss.append(new_ladderon.make_ref())
    c_pos = len(ss) - 1
    for idx_s in m_idx_cs:
        lut[idx_s].append(c_pos)
    # print(f"got {ss} with {lut}")
    assert replaced_cnt > 1
    components.append(new_ladderon)
    return ss, lut, replaced_cnt - 1

def find_ladderpath(ss: List[str]) -> Tuple[int, int, int, List[Ladderon]]:
    str_lens = [len(s) for s in ss]
    total_str_len = sum(str_lens)
    print(f'{len(ss)} strings, max_str_len: {max(str_lens)}, total_str_len: {total_str_len}')
    total_start_time = time()
    components = [Ladderon(i, s) for i, s in enumerate(ss)]
    ss = [LadderonRef(l, 0, len(l.STR), l.STR) for l in components]

    lp = 0
    luts = []
    component_start_time = time()
    css = find_components(ss)
    component_end_time = time()
    need_recompute = False
    level = len(css) - 1
    new_level = True
    print(f'Start from {level} level, components time: {component_end_time - component_start_time}s')
    while level > 0:
        if need_recompute:
            luts = []
            component_start_time = time()
            last_duration = component_start_time - component_end_time
            css = find_components(ss)
            component_end_time = time()
            # print(f'after {last_duration}s, Recompute components using {component_end_time - component_start_time}s')
            need_recompute = False
            assert len(css) - 1 <= level
            if level != len(css) - 1:
                new_level = True
            level = len(css) - 1
        if new_level:
            level_component_cnt = 0
            process_start_time = time()
        new_level = False
        cs = [Pattern(c, 0, idxs) for c, idxs in css[level].items()]
        cs = sorted(cs, key=lambda x: x.key(), reverse=True)
        while True:
            if not cs:
                new_level = True
                break
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
            cs = sorted(updated_cs + left_cs, key=lambda x: x.key(), reverse=True)
            if max_cs is None:
                new_level = True
                break
            assert max_cs.s == cs[0].s
            level_component_cnt += 1
            if level_component_cnt % 1000 == 0:
                now_time = time()
                print(f'processing {level} level, {len(ss)} strings, {level_component_cnt} components using {now_time - process_start_time}s')
                process_start_time = now_time
            ss, lut, new_lp = find_ladderpath_with_cs(ss, max_cs, components)
            lp += new_lp
            luts.append(lut)
            cs = cs[1:]
            if time() - component_end_time > component_end_time - component_start_time:
                need_recompute = True
                break
        if new_level:
            if level_component_cnt > 0:
                print(f'processed {level} level, {len(ss)} strings, {level_component_cnt} components')
            level -= 1
    lp += find_ladderpath_of_level0(ss, components)
    duration = time() - total_start_time
    print(f'LP: {lp}, order: {total_str_len - lp}, size: {total_str_len}, time: {duration}s')
    return lp, total_str_len, duration, components


def test_sample():
    test_s = 'acsccsaascascaaaacssscscscasasacssacssaaaacsccsaascascaaaacssscscscasasacssacssaaa'
    test_lp, _, _, comps = find_ladderpath([test_s])
    print(comps)
    assert test_lp == 25, f'Test LP should be 25, but got {test_lp}'
    print("Test passed")

def save_specie_str():
    import pandas as pd

    data = pd.read_csv('../six_species.txt', sep='\t')
    # print([f'{s}: {len(data[data["Species"] == s])}' for s in set(data['Species'])])
    
    # ECOLI -- strs: 4529, LP: 480530, order: 907347, size: 1387877, time: 1637.6894958019257s
    #                      LP: 480557, order: 907320, size: 1387877, time: 760.0485439300537s
    # CAEEL -- strs: 4381, LP: 777104, order: 1533359, size: 2310463, time: 2489.757828950882s
    # YEAST -- strs: 6727, LP: 952637, order: 2072791, size: 3025428, time: 4152.814738988876s
    # ARATH -- strs: 16215, 
    # MOUSE -- strs: 17119, 
    # HUMAN -- strs: 20386, 

    from sys import argv
    specie = argv[1]
    assert specie in ['ECOLI', 'CAEEL', 'YEAST', 'ARATH', 'MOUSE', 'HUMAN']
    print(f"Compute LP of {specie}")
    specie_data = data[data['Species'] == specie]
    specie_strs = specie_data['Sequence'].tolist()

    with open(f"{specie}_str.json", "w") as f:
        json.dump(specie_strs, f, indent=2)

def compute_specie_lp():
    from sys import argv
    specie = argv[1]
    assert specie in ['ECOLI', 'CAEEL', 'YEAST', 'ARATH', 'MOUSE', 'HUMAN']
    with open(f"{specie}_str.json", "r") as f:
        specie_strs = json.load(f)

    _, _, _, comps = find_ladderpath(specie_strs)
    print(f"{specie} -- strs: {len(specie_strs)}")

    with open(f"../species_lp/{specie}.json", "w") as f:
        json.dump([c.asdict() for c in comps], f, indent=2)

if __name__ == '__main__':
    # test_sample()
    # save_specie_str()
    compute_specie_lp()
