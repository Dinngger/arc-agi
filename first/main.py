from data import *
from concept import *
from reasoning import *
from paint import *
from registration import *
from subimage import *
from region_map import *

def mirror_solver(data: Data):
    hypothesis = [PositionMap(0), PositionMap(1)]
    for h in hypothesis:
        if check_hypothesis(data, h):
            return h
    return None

def conv_solver(data: Data):
    return ColorMap.get_all_patterns(data.train)

def tester(train=True):
    easy_ks = ['5c2c9af4', '623ea044', 'dbc1a6ce', 'bdad9b1f', '1e0a9b12',
               'a48eeaf7', 'bda2d7a6', 'f35d900a', '264363fd', 'c9f8e694',
               '60b61512', 'f8b3ba0a', '4938f0c2', 'd406998b', '868de0fa',
               'ff805c23', 'e8593010', '017c7c7b', 'ec883f72', '150deff5',
               '56dc2b01', 'aabf363d', 'ba97ae07', '05269061', '2013d3e2',
               '7ddcd7ec', 'ef135b50', '3befdf3e']
    registration_ks = ['7df24a62', 'a1570a43', 'cf98881b', '681b3aeb', '0b148d64',
                       '952a094c']
    subimage_ks = ['c444b776', '6ecd11f4', 'c909285e', '88a10436']
    data = get_data(train)
    correct_cnt = 0
    failure_cnt = 0
    for k, v in data.items():
        if k in easy_ks + registration_ks + subimage_ks:
            f = globals()[f'solve_{k}']
        else:
            f = mirror_solver(v)
        if f is None:
            f = conv_solver(v)
        if f is not None:
            success = True
            for test_case in v.train + v.test:
                if f(test_case.input) != test_case.output:
                    print(f"Failed on {k}")
                    print("expected:")
                    print(test_case.output)
                    print("got:")
                    print(f(test_case.input))
                    failure_cnt += 1
                    success = False
                    break
            if success:
                print(f"{k} solved")
                correct_cnt += 1
    print(f"Failures: {failure_cnt} / {failure_cnt + correct_cnt}")
    print(f"Accuracy: {correct_cnt} / {len(data)}")

if __name__ == '__main__':
    tester(train=True)
