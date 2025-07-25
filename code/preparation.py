from Qcontrol import *
from Qint import *
import numpy as np

def coset_preparation(qint:Qint, 
                      m:int)->Qcontrol:
    qt = qint.copy()
    added_bit = "0"*m
    qt.insert(added_bit, pos=len(qt))
    for i in range(m):
        qc = Qcontrol.qalloc(1, "X")
        qr = controlled_by(qc, qt, [0, 2**i * qt.module], BinaryInt.__add__)

        qt, outcome = qr.measure_controls([0], "X")

        if outcome == Cvalue(1, 1):
            qt.comparison_neg(2**i * qt.module)
        
    return qt

def oblivous_runways(qint:Qint,
                     m:int,
                     target_lst:List[int],
                     pos: int) -> Qint:
    if m > len(target_lst):
        raise ValueError("Oblivious runways qubits must be fewer than the target qubits")
    q_result = qint.copy()
    q_result.insert(m*"0", pos, basis="X")
    offsets = np.arange(2**m)
    offsets = -offsets
    controls = np.arange(pos+m-1, pos-1, -1)
    target_lst = np.array(target_lst)
    target_lst += m
    q_result.controlled_add(controls, offsets, target_lst)
    return q_result


