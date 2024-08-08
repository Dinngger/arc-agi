# Author: Dinger
# Data: 2024-08-08


from collections import defaultdict
from typing import List, Dict, Tuple

def find_components(ss: List[str]) -> Tuple[Dict[str, List[Tuple[int, int]]], int]:
    last_cs = defaultdict(list)
    for idx_s, s in enumerate(ss):
        for idx_c, c in enumerate(s):
            last_cs[c].append((idx_s, idx_c))
    level = 0
    while True:
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
        level += 1
    return last_cs, level

def find_ladderpath2(ss: List[str]) -> int:
    cs, level = find_components(ss)
    # print(f'processing {level} level, ss: {ss}, cs: {cs}')
    if level == 0:
        return sum(len(s) for s in ss)
    cs0 = max(cs.items(), key=lambda x: len(x[1]))
    c = cs0[0]
    assert len(c) == level + 1
    idx_cs = [[] for _ in range(len(ss))]
    for idx_s, idx_c in cs0[1]:
        idx_cs[idx_s].append(idx_c)
    new_ss = [c]
    replaced_cnt = 0
    for s, idxs in zip(ss, idx_cs):
        last_i = 0
        for i in sorted(idxs):
            if i < last_i:
                continue
            if i > last_i:
                new_ss.append(s[last_i:i])
            replaced_cnt += 1
            last_i = i + len(c)
        if last_i < len(s):
            new_ss.append(s[last_i:])
    assert replaced_cnt > 1
    if replaced_cnt > 2:
        print(f'{c}({replaced_cnt-1}), ', end='')
    else:
        print(f'{c}, ', end='')
    return find_ladderpath2(new_ss) + replaced_cnt - 1

from sys import argv
if len(argv) < 2:
    s = 'acsccsaascascaaaacssscscscasasacssacssaaaacsccsaascascaaaacssscscscasasacssacssaaa'
    s = 'MVVSAGPWSSEKAEMNILEINEKLRPQLAENKQQFRNLKERCFLTQLAGFLANRQKKYKYEECKDLIKFMLRNERQFKEEKLAEQLKQAEELRQYKVLVHSQERELTQLREKLREGRDASRSLNEHLQALLTPDEPDKSQGQDLQEQLAEGCRLAQQLVQKLSPENDEDEDEDVQVEEDEKVLESSAPREVQKAEESKVPEDSLEECAITCSNSHGPCDSIQPHKNIKITFEEDKVNSTVVVDRKSSHDECQDALNILPVPGPTSSATNVSMVVSAGPLSSEKAEMNILEINEKLRPQLAEKKQQFRSLKEKCFVTQLAGFLAKQQNKYKYEECKDLIKSMLRNELQFKEEKLAEQLKQAEELRQYKVLVHSQERELTQLREKLREGRDASRSLNEHLQALLTPDEPDKSQGQDLQEQLAEGCRLAQHLVQKLSPENDEDEDEDVQVEEDEKVLESSSPREMQKAEESKVPEDSLEECAITCSNSHGPCDSNQPHKNIKITFEEDKVNSSLVVDRESSHDECQDALNILPVPGPTSSATNVSMVVSAGPLSSEKAEMNILEINEKLRPQLAEKKQQFRSLKEKCFVTQVACFLAKQQNKYKYEECKDLLKSMLRNELQFKEEKLAEQLKQAEELRQYKVLVHSQERELTQLREKLREGRDASRSLNEHLQALLTPDEPDKSQGQDLQEQLAEGCRLAQHLVQKLSPENDNDDDEDVQVEVAEKVQKSSSPREMQKAEEKEVPEDSLEECAITCSNSHGPYDSNQPHRKTKITFEEDKVDSTLIGSSSHVEWEDAVHIIPENESDDEEEEEKGPVSPRNLQESEEEEVPQESWDEGYSTLSIPPERLASYQSYSSTFHSLEEQQVCMAVDIGRHRWDQVKKEDQEATGPRLSRELLAEKEPEVLQDSLDRCYSTPSVYLGLTDSCQPYRSAFYVLEQQRVGLAVDMDEIEKYQEVEEDQDPSCPRLSRELLAEKEPEVLQDSLDRCYSTPSGYLELPDLGQPYRSAVYSLEEQYLGLALDVDRIKKDQEEEEDQGPPCPRLSRELLEVVEPEVLQDSLDRCYSTPSSCLEQPDSCQPYRSSFYALEEKHVGFSLDVGEIEKKGKGKKRRGRRSKKKRRRGRKEGEEDQNPPCPRLSRELLAEKEPEVLQDSLDRWYSTPSVYLGLTDPCQPYRSAFYVLEQQRVGLAVDMDEIEKYQEVEEDQDPSCPRLSRELLAEKEPEVLQDSLDRCYSTPSGYLELPDLGQPYRSAVYSLEEQYLGLALDVDRIKKDQEEEEDQGPPCPRLSRELLEVVEPEVLQDSLDRCYSTPSSCLEQPDSCQPYRSSFYALEEKHVGFSLDVGEIEKKGKGKKRRGRRSKKKRRRGRKEGEEDQNPPCPRLNSVLMEVEEPEVLQDSLDRCYSTPSMYFELPDSFQHYRSVFYSFEEQHITFALDMDNSFFTLTVTSLHLVFQMGVIFPQ'
else:
    s = argv[1]
print(f'ladderpath-index={find_ladderpath2([s])}')
