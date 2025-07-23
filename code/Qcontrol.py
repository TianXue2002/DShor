import numpy as np
from Bint import *
from typing import List, Union, Callable
from Qint import Qint

class Cvalue():
    def __init__(self,
                 value: int,
                 length: int):
        self.length = length
        bin_str = bin(value)[2:].zfill(length)
        self.binary = bin_str
        self.value = value

class Qcontrol():
    def __init__(self, 
                 values: List[Cvalue], 
                 amps: List[np.complexfloating], 
                 length: int):
        self.values = values
        self.amps = amps
        self.length = length
    
    def qalloc(num, basis):
        if basis == "X":
            values = list(range(0,2**num))
            values = [Cvalue(value, num) for value in values]
            amps = np.repeat(1/2**(num/2), 2**num)
            module = 2**num
            length = num
        if basis == "Z":
            values = [Cvalue(0, num)]
            amps = [1]
            module = 2**num
            length = num
        return Qcontrol(values, amps, length)
    
class Qregister():
    def __init__(self, 
                 values: List[Union[Cvalue, BinaryInt]],
                 amps: List[np.complex128],
                 module: int,
                 length: int):
        self.values = values
        self.amps = amps
        self.module = module
        self.length = length

    def __str__(self):
        return "\n".join(f"{amp} → {val[0].binary}|{val[1].binary}" for amp, val in zip(self.amps, self.values))

def controlled_by(qc: Union[int, Qcontrol],
                qt:Qint,
                offset:Union[int, List[int]],
                f: Callable[[BinaryInt, int], BinaryInt]):
    if qc == 0:
            pass
    elif qc == 1:
        if isinstance(offset, int):
            result_values = [f(xi, offset).value for xi in qt.values]
            result_amps = qt.amps
            result_length = qt.length
            result_module = qt.module
            return Qint(result_values, result_amps, result_module, result_length)
        else:
            raise ValueError("Cannot load more than 1 integer with classical control")

    elif isinstance(qc, Qcontrol):
        if isinstance(offset, List):
            # for c, t in zip(qc.values, qt.values):
            #     print(type(c << qt.length))
            #     print(type(f(t, offset[c.value])))
            #     print((c << qt.length) + f(t, offset[c.value]))
            result_values = [[c, (f(t, offset[c.value]))] 
                    for c in qc.values for t in qt.values]
            result_amps = [c_amp * t_amp for c_amp in qc.amps for t_amp in qt.amps]
            result_length = qc.length+qt.length
            result_module = qt.module
            return Qregister(result_values, result_amps, result_module, result_length)
        else:
            raise ValueError("A single integer table can be loaded by a classical control")
    else:
        raise ValueError("Invalid Control. Controls is either classical or quantum.")
    