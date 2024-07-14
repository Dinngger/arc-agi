

class Image:
    def __init__(self, list):
        self.list = list
        self.height = len(list)
        self.width = len(list[0])
    def in_bound(self, i, j):
        return 0 <= i < self.height and 0 <= j < self.width
    def __getitem__(self, index) -> int:
        assert len(index) == 2
        if isinstance(index[0], slice) or isinstance(index[1], slice):
            return Image([row[index[1]] for row in self.list[index[0]]])
        if not self.in_bound(index[0], index[1]):
            raise IndexError(f"Index {index} out of bound")
        return self.list[index[0]][index[1]]
    def __setitem__(self, index, value):
        assert len(index) == 2
        if not self.in_bound(index[0], index[1]):
            raise IndexError(f"Index {index} out of bound")
        self.list[index[0]][index[1]] = value
    def __eq__(self, value) -> bool:
        return self.list == value.list
    def __repr__(self) -> str:
        s = ''
        for row in self.list:
            s += ''.join(str(x) for x in row) + '\n'
        return s[:-1]
    def self_generate(self, f):
        return Image([[f(self, i, j) for j in range(self.width)]
                      for i in range(self.height)])
    @staticmethod
    def generate(f, h, w):
        img = [[f(i, j) for j in range(w)]
               for i in range(h)]
        return Image(img)
    @staticmethod
    def zeros(h, w):
        return Image.generate(lambda i, j: 0, h, w)
