from data import *
from concept import *
from reasoning import *

def mirror_solver(data: Data):
    hypothesis = [PositionMap(0), PositionMap(1)]
    for h in hypothesis:
        if check_hypothesis(data, h):
            return h
    return None

def conv_solver(data: Data):
    return ColorMap.get_all_patterns(data.train)

def test_solver(train=True):
    data = get_data(train)
    correct_cnt = 0
    failure_cnt = 0
    for k, v in data.items():
        f = mirror_solver(v)
        if f is None:
            f = conv_solver(v)
        if f is not None:
            success = True
            for test_case in v.test:
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
    test_solver(train=True)
