# Author: Dinger
# Data: 2024-08-07
# Find the minimum ladderpath-index of a string.

from collections import Counter
import random

def find_ladderpath(s: str):
    ss = [s]
    cnt = 0
    min_lp = len(s)
    while ss:
        assert cnt < 65, 'need a new coding method'
        new_ss = []
        for s in ss:
            min_lp = min(min_lp, cnt + len(s))
            all_2_grams = [s[i:i+2] for i in range(len(s)-1)]
            count = Counter(all_2_grams)
            for k,v in count.items():
                if v > 1:
                    new_s = s.replace(k, str(chr(cnt)))  # only A-z are allowed in s
                    new_ss.append(new_s)
        if new_ss:
            ss = new_ss
        lens = [len(s) for s in ss]
        min_len = min(lens)
        sampled_ss = []
        for margin in range(5):
            m_ss = [s for s in ss if len(s) == min_len + margin]
            if len(m_ss) > 50:
                m_ss = random.sample(m_ss, 50)
            sampled_ss.extend(m_ss)
        ss = sampled_ss
        if not new_ss:
            min_lp = min(min_lp, cnt + min_len)
            return min_lp
        cnt += 1

from sys import argv
if len(argv) < 2:
    s = 'acsccsaascascaaaacssscscscasasacssacssaaaacsccsaascascaaaacssscscscasasacssacssaaa'
    print(f'using default string: {s}')
else:
    s = argv[1]
print('ladderpath-index =', find_ladderpath(s))
