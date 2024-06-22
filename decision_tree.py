
import numpy as np

DEBUG = False

class LinearRegression:
    d = 10
    @staticmethod
    def one_hot(x):
        return np.eye(LinearRegression.d)[x]
    def __init__(self, x, y):
        assert len(x.shape) == 2
        assert len(y.shape) == 1
        assert x.shape[0] == y.shape[0]
        self.m, self.n = x.shape
        self.original_x = x
        self.original_y = y
        self.x = np.eye(self.d)[x]  # m x n x d
        self.y = np.eye(self.d)[y]  # m x d
        self.compute_A()    # n
        self.compute_b()    # d
        if DEBUG: print('      ', self)
    def __str__(self):
        pf = lambda x: f'{x:.2f}' if abs(x) > 1e-6 else '0'
        return '[' + ' '.join([pf(x) for x in self.A]) + ']x + [' + \
               ' '.join([pf(x) for x in self.b]) + ']'
    def compute_A(self):
        XX = np.zeros((self.n, self.n))
        for i in range(self.d):
            sx = self.x[:, :, i].mean(axis=0)
            for j in range(self.m):
                XX += np.outer(self.x[j, :, i], self.x[j, :, i] - sx)
        XY = np.zeros(self.n)
        for i in range(self.d):
            sy = self.y[:, i].mean()
            for j in range(self.m):
                XY += self.x[j, :, i] * (self.y[j, i] - sy)
        self.A, residuals, rank, s = np.linalg.lstsq(XX, XY, rcond=None)
    def compute_b(self):
        self.b = np.zeros(self.d)
        for i in range(self.d):
            self.b[i] = self.y[:, i].mean() - self.x[:, :, i].mean(axis=0).dot(self.A)
    def predict(self, x):
        assert len(x.shape) == 2
        x = np.eye(self.d)[x].transpose(0, 2, 1)    # m x d x n
        y = x @ self.A + self.b    # m x d
        return y.argmax(axis=1)
    def score(self):
        s = np.abs(self.y - self.x.transpose(0, 2, 1) @ self.A - self.b).sum()
        return s

class Node:
    def __init__(self, x, y):
        self.n = x.shape[0]
        self.d = x.shape[1]
        self.x = x
        self.y = y
        self.possible_y = np.unique(self.y)
    def mask(self, x, idx):
        # 0 1 2
        # 3 4 5
        # 6 7 8
        if not isinstance(x, np.ndarray):
            x = np.array([x])
        assert len(x.shape) == 2
        if idx >= 0:
            res = x[:, idx] == 0
        elif idx == -1:
            res = np.logical_and(x[:, 4], np.count_nonzero(x[:, [1, 3, 5, 7]], axis=1) >= 2)
        elif idx == -2:
            res = np.count_nonzero(x[:, [1, 3, 5, 7]], axis=1) < 4
        elif idx == -3:
            res = np.count_nonzero(x[:, [1, 3, 5, 7]], axis=1) >= 2
        elif idx == -4:
            res = np.count_nonzero(x[:, [1, 7]], axis=1) >= 2
        elif idx == -5:
            res = np.count_nonzero(x[:, [3, 5]], axis=1) >= 2
        if x.shape[0] == 1:
            return res[0]
        return res
    def p(self):
        cnt = {y:0 for y in self.possible_y}
        for i in self.y:
            cnt[i] += 1
        return [c / self.n for c in cnt.values()]
    def relative(self, i):
        cnt = 0
        for x, y in zip(self.x, self.y):
            if y == x[i]:
                cnt += 1
        return 1 - cnt / self.n
    def linear_regression(self):
        self.lr = LinearRegression(self.x, self.y)
        return self.lr.score()
    def predict(self, x):
        if hasattr(self, 'left'):
            if self.mask(x, self.split_type):
                return self.left.predict(x)
            else:
                return self.right.predict(x)
        else:
            return self.lr.predict(np.array([x]))[0]
    def gini(self):
        if self.n == 0:
            return 0
        # gini = 1 - sum([p**2 for p in self.p()])
        # r = min([self.relative(i) for i in range(self.d)])
        return self.linear_regression()
    def try_split(self, split_type):
        mask = self.mask(self.x, split_type)
        a = Node(self.x[mask], self.y[mask])
        b = Node(self.x[~mask], self.y[~mask])
        return (a.gini() * a.n + b.gini() * b.n) / self.n
    def split(self, depth=0):
        if depth >= 10:
            print('Max depth reached')
            return
        minimal_gini = self.gini()
        if DEBUG: print(f'Splitting node with gini = {minimal_gini:.5f}')
        if minimal_gini < 1e-6:
            return minimal_gini
        best_feature_idx = None
        for i in range(-5, 9):
            gini = self.try_split(i)
            if DEBUG: print(f'  Trying feature {i}, gini = {gini:.5f}')
            if gini < minimal_gini:
                minimal_gini = gini
                best_feature_idx = i
        if best_feature_idx is None:
            return
        self.split_type = best_feature_idx
        mask = self.mask(self.x, best_feature_idx)
        self.left = Node(self.x[mask], self.y[mask])
        if self.left.split(depth+1) is None:
            return
        self.right = Node(self.x[~mask], self.y[~mask])
        if self.right.split(depth+1) is None:
            return
        return minimal_gini
    def __str__(self, level=0):
        s = '  '*level + f'Node with {self.n} samples\n'
        if hasattr(self, 'left'):
            s += '  '*(level+1) + f'Split on feature {self.split_type}\n'
            s += self.left.__str__(level+1) + '\n'
            s += self.right.__str__(level+1)
        else:
            s += '  '*(level+1) + f'No split, gini = {self.gini():.5f}, lr = {self.lr}'
        return s


if __name__ == '__main__':
    from data import *
    from concept import *
    from reasoning import *
    data = get_data(True)['7f4411dc']
    node = ColorMap.get_all_patterns(data.train)
