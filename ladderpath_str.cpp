#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <set>

#define MAX_MARGIN 20
int find_ladderpath(std::string string) {
    using ts = std::vector<int>;
    ts s0(string.begin(), string.end());
    int init_cnt = *std::max_element(s0.begin(), s0.end());
    int cnt = init_cnt;
    printf("init_cnt: %d\n", init_cnt);
    using tss = std::vector<ts>;
    tss ss = {s0};
    int min_lp = s0.size();
    while (true) {
        tss new_ss;
        int min_len = ss[0].size();
        for (auto s : ss) {
            min_lp = std::min(min_lp, cnt - init_cnt + int(s.size()));
            std::multiset<std::pair<int, int>> all_2_grams;
            for (int i = 0; i < s.size() - 1; i++)
                all_2_grams.insert({s[i], s[i+1]});
            for (auto k : all_2_grams) {
                int v = all_2_grams.count(k);
                if (v <= 1)
                    continue;
                if (s.size() - v > min_len + MAX_MARGIN)
                    continue;
                ts new_s;
                bool jump_next = false;
                for (int i = 0; i < s.size() - 1; i++) {
                    if (jump_next)
                        jump_next = false;
                    else if (s[i] == k.first && s[i+1] == k.second) {
                        new_s.push_back(cnt);
                        jump_next = true;
                    } else
                        new_s.push_back(s[i]);
                }
                if (!jump_next)
                    new_s.push_back(s.back());
                min_len = std::min(min_len, int(new_s.size()));
                new_ss.push_back(new_s);
            }
        }
        if (!new_ss.empty())
            ss = new_ss;
        tss sampled_ss;
        for (int margin = 0; margin < MAX_MARGIN; margin++) {
            tss m_ss;
            for (auto s : ss) {
                if (s.size() == min_len + margin)
                    m_ss.push_back(s);
            }
            if (m_ss.size() > 20) {
                // randomly sample 20
                std::random_shuffle(m_ss.begin(), m_ss.end());
                sampled_ss.insert(sampled_ss.end(), m_ss.begin(), m_ss.begin() + 20);
            } else {
                sampled_ss.insert(sampled_ss.end(), m_ss.begin(), m_ss.end());
            }
        }
        ss = sampled_ss;
        if (new_ss.empty()) {
            min_lp = std::min(min_lp, cnt - init_cnt + min_len);
            return min_lp;
        }
        cnt++;
        printf("processed %d levels, this level has %d new strings, min_lp: %d\n", cnt, int(new_ss.size()), min_lp);
    }
    return -1;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <string>" << std::endl;
        return 1;
    }
    std::string s(argv[1]);
    int lp = find_ladderpath(s);
    std::cout << "ladderpath-index = " << lp << std::endl;
    return 0;
}
