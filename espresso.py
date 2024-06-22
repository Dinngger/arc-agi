from pyeda.boolalg.espresso import (DTYPE, FTYPE, RTYPE, espresso, set_config)
from pyeda.boolalg.expr import exprvar
from pyeda.boolalg.minimization import _cover2exprs

import numpy as np
from data import *
from concept import *
from reasoning import *
data = get_data(True)['42a50994']
patterns = ColorMap.get_all_patterns(data.train)
x_num = len(next(iter(patterns.keys())))
print(x_num)

ninputs = x_num * 4
noutputs = 4
intype = FTYPE | RTYPE
input_labels = sum([[f'x{i}_{j}' for j in range(4)] for i in range(x_num)], [])
input_vars = sum([[exprvar(f'x{i}', j) for j in range(4)] for i in range(x_num)], [])
output_labels = [f'y{i}' for i in range(4)]

_INCODE = {"0": 1, "1": 2, "-": 3}
_OUTCODE = {"0": 0, "1": 1, "-": 2}
cover = set()
for i, o in patterns.items():
    inputs = ''.join([f'{ii:04b}' for ii in i])
    outputs = f'{o:04b}'
    invec = tuple(_INCODE[c] for c in inputs)
    outvec = tuple(_OUTCODE[c] for c in outputs)
    cover.add((invec, outvec))

opt_cover = espresso(ninputs, noutputs, cover, intype)
_cover2exprs(input_vars, noutputs, cover)
