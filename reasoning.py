from data import Data


def check_hypothesis(data: Data, hypothesis):
    for s in data.train:
        if hypothesis(s.input) != s.output:
            return False
    return True


def patterns_simplify(patterns):
    pass

