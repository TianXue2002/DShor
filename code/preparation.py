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
                     m:int) -> Qint:
    qc = Qcontrol.qalloc(m, "X")
    qr = 1
    pass

