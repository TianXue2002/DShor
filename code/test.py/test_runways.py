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

def test_oblivious_runways(k, m, length):
    module = 2**length-2
    values = np.arange(module)
    amps = np.zeros(2**length, dtype=np.complex128)
    amps[values] = 1/np.sqrt(len(values))
    q = Qint(values, amps, module, length)
    pos = 2
    # print(q)
    targets = list(range(2,length))
    qr = oblivous_runways(q, m, targets, pos)
    qr = qr + 2**(pos + m) * (k//(2**(len(q) - pos)))
    qr = qr + (k%(2**(len(q) - pos)))
    # for value in qr.values:
    #     updated_value_up = value + 2**(pos + m) * (k//(2**(len(q) - pos)))
    #     updated_value = updated_value_up + (k%(2**(len(q) - pos)))
    #     qr.update_value(value, updated_value)

    result_value = []
    result_amps = np.zeros(2**length, np.complex128)
    prob_lst = np.zeros(2**length)
    amps = qr.amps
    for value in qr.values:
        up_half = value[m+2:]
        low_half = value[:m+2]
        new_value = 2**(2) * up_half.value + low_half.value
        new_value = new_value % 2**(length)
        # print(BinaryInt(new_value, length),"bit")
        prob_lst[new_value] += np.abs(qr.amps[value.value])**2
        new_value = BinaryInt(new_value, length)
        if new_value not in result_value:
            result_value.append(new_value)
    # print(result_amps)
    result_amps = np.sqrt(prob_lst)
    qr = Qint(result_value, result_amps, module, length)
    q_ref = q+k
    print(q_ref@qr)
    return (q_ref@qr)**2
m = 2

test_oblivious_runways(0, m, m+2)
l = 6
error = np.zeros(l)
m_lst = np.arange(2,2+l)
k = np.random.randint(2**(m+2))
for i in range(l):
    m = m_lst[i]
    k = int(k)
    error[i] = 1- test_oblivious_runways(k, m, m+2)
plt.semilogy(m_lst, error)
plt.ylabel("error")
plt.xlabel("number of runway qubits")