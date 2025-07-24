import importlib

import Qint
import Bint
import numpy as np
import Qcontrol
import preparation
from functools import partial


importlib.reload(Bint)
importlib.reload(Qint)
importlib.reload(Qcontrol)
importlib.reload(preparation)


from Bint import BinaryInt
from Qint import *
from Qcontrol import *
from preparation import *

qc = Qcontrol.qalloc(2, "X")
length = 2
module = 2**length
lst = list(range(2**length))
amps = np.repeat(1/np.sqrt(len(lst))*1j, len(lst))
offset = [0, 1, 2, 3]
pos_lst = [0,1]

m = 5

qt = Qint(lst, amps, module, length)

qr = controlled_by(qc, qt, offset, partial(Bint.modular_add, N = qt.module))
print(qr)
qr, outcome = qr.measure_controls([0,1], "X")
print(outcome)
print(qr)
# qr = coset_preparation(qt, m)
