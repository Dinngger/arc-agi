# Author: Dinger
# Data: 2024-08-07
# Find the minimum ladderpath-index of a string.

from collections import Counter
import random

def find_ladderpath(s: str):
    s = tuple([ord(c) for c in s])
    ss = [s]
    init_cnt = cnt = max(s)
    print(f'init cnt = {cnt}')
    min_lp = len(s)
    max_margin = 5
    while True:
        new_ss = []
        min_len = len(ss[0])
        for s in ss:
            min_lp = min(min_lp, cnt - init_cnt + len(s))
            all_2_grams = [s[i:i+2] for i in range(len(s)-1)]
            count = Counter(all_2_grams)
            for k,v in count.items():
                if v > 1:
                    if len(s) - v > min_len + max_margin:
                        continue
                    new_s = []
                    jump_next = False
                    for i in range(len(s)-1):
                        if jump_next:
                            jump_next = False
                        elif s[i:i+2] == k:
                            new_s.append(cnt)
                            jump_next = True
                        else:
                            new_s.append(s[i])
                    if not jump_next:
                        new_s.append(s[-1])
                    min_len = min(min_len, len(new_s))
                    new_ss.append(tuple(new_s))
        if new_ss:
            ss = new_ss
        sampled_ss = []
        for margin in range(max_margin):
            m_ss = [s for s in ss if len(s) == min_len + margin]
            if len(m_ss) > 20:
                m_ss = random.sample(m_ss, 20)
            sampled_ss.extend(m_ss)
        ss = sampled_ss
        if not new_ss:
            min_lp = min(min_lp, cnt - init_cnt + min_len)
            return min_lp
        cnt += 1
        print(f'processed {cnt} levels, this level has {len(new_ss)} new strings, min_lp = {min_lp}')

from sys import argv
if len(argv) < 2:
    s = 'acsccsaascascaaaacssscscscasasacssacssaaaacsccsaascascaaaacssscscscasasacssacssaaa'
    print(f'using default string: {s}')
else:
    s = argv[1]
print('ladderpath-index =', find_ladderpath(s))
