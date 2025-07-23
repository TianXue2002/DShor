import numpy as np
from Bint import BinaryInt
from typing import List, Tuple, Callable, Union
class Qint():
    def __init__(self, 
                 values: Union[List[int], List[BinaryInt]],
                 amps: List[np.complexfloating], 
                 module: int,
                 length: int):
        qint_lst = []
        for value in values:
            if isinstance(value, int):
                bint = BinaryInt(value % module, module, length)
                qint_lst.append(bint)
            elif isinstance(value, BinaryInt):
                if value.module != module:
                    raise ValueError("data and qubit have different modules")
                bint = value
        self.values = qint_lst
        self.amps = amps
        self.length = length
        self.module = module
        if abs(sum(np.abs(amps)**2)-1)>=1e-7:
            raise ValueError("Unnormalized state")
    
    def __str__(self):
        return "\n".join(f"{amp} → {val.binary}" for amp, val in zip(self.amps, self.values))
    
    def __lshift__(self, offset):
        

    def update(self, values):
        qint_lst = []
        for value in values:
            bint = BinaryInt(value, self.module, self.length)
            qint_lst.append(bint)
        self.values = qint_lst

def qalloc(num:int, basis:str):
    if basis == "X":
        values = list(range(0,2**num))
        amps = np.repeat(1/2**(num/2), 2**num)
        module = 2**num
        length = num
    if basis == "Z":
        values = [0]
        amps = [1]
        module = 2**num
        length = num
    return Qint(amps, values, module, length)