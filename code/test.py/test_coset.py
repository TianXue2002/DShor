import importlib

import Qint
import Bint
import numpy as np
import Qcontrol
import preparation
from functools import partial
import matplotlib.pyplot as plt

importlib.reload(Bint)
importlib.reload(Qint)
importlib.reload(Qcontrol)
importlib.reload(preparation)


from Bint import BinaryInt
from Qint import *
from Qcontrol import *
from preparation import *

def test_coset(m):
    length = 10
    module = np.random.randint(0, 2**length-1)
    lst = np.arange(module,dtype=int)
    amps = np.zeros(2**length, dtype=np.complex128)
    amps[lst] = np.repeat(1/np.sqrt(len(lst))*1j, len(lst))
    qt = Qint(lst, amps, module, length)
    q_coset = coset_preparation(qt, m)

    k = 1
    qc = Qcontrol.qalloc(k, "X")
    offset = np.arange(2**k,dtype=int)
    qr_coset = controlled_by(qc, q_coset, offset, BinaryInt.__add__)
    qr_uncoset = controlled_by(qc, qt, offset, partial(modular_add, N = module))

    ref_amps = np.zeros(2**(length + m + k), dtype=np.complex128)
    ref_value = []
    for value in qr_uncoset.values:
        cvalue = value[0]
        data = value[1]
        for s in range(2**m):
            cur_data = data.copy()
            cur_data.length += m
            cur_data = cur_data + s*module
            ref_value.append([cvalue, cur_data])
            amp_index = 2**len(cur_data) * cvalue.value  + cur_data.value
            ref_amps[amp_index] = qr_uncoset.amps[data.value]/(2**(m/2))
    q_ref = Qregister(ref_value, ref_amps, module, length + m + k)
    return 1 - np.abs(q_ref@qr_coset)

result_lst = np.zeros(10)
m_lst = np.arange(10)
for m in range(10):
    result_lst[m] = test_coset(m)
plt.semilogy(result_lst)
plt.semilogy(1/(2**m_lst))
plt.legend(["coset error", r"$2^{-m}$"])
plt.ylabel("error")