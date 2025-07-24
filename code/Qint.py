import numpy as np
from Bint import BinaryInt
from typing import List, Tuple, Callable, Union
class Qint():
    def __init__(self, 
                 values: Union[List[int], List[BinaryInt]],
                 amps: List[np.complexfloating], 
                 module: int,
                 length: int):
        if len(amps) != 2**length:
            raise ValueError("Didn't specify all amplitudes")
        
        qint_lst = []
        for value in values:
            if isinstance(value, int) or isinstance(value, np.int64):
                if value >= 2**length:
                    raise ValueError("loading a value greater than the register can hold")
                bint = BinaryInt(value, length)
                qint_lst.append(bint)

            if isinstance(value, BinaryInt):
                if value.length >= 2**length:
                    raise ValueError("loading a value greater than the register can hold")
                qint_lst.append(value)
        self.values = qint_lst
        self.amps = amps
        self.length = length
        self.module = module
        if abs(sum(np.abs(amps)**2)-1)>=1e-7:
            raise ValueError("Unnormalized state")
    
    def __str__(self):
        output = ""
        for value in self.values:
            output += f"{self.amps[value.value]} → {value.binary}\n"
        return output
    
    def __lshift__(self, offset):
        result_values = [value << offset for value in self.values]
        result_length = self.length + offset
        return Qint(result_values, self.amps, self.module, result_length)

    def __len__(self):
        return self.length

    def __matmul__(self,
                   other):
        amp1 = self.amps
        amp2 = other.amps
        return np.vdot(amp1, amp2)
    

    def update(self, values):
        qint_lst = []
        for value in values:
            bint = BinaryInt(value, self.length)
            qint_lst.append(bint)
        self.values = qint_lst

    def copy(self):
        copy_values = [value.copy() for value in self.values]
        copy_amps = self.amps.copy()
        return Qint(copy_values, copy_amps, self.module, len(self))
    
    def update_length(self, additional_length):
        for value in self.values:
            value.length += additional_length

    def insert(self,
               bit: Union[int, str],
               pos = 0):
        if isinstance(bit, str):
            self.length += len(bit)
        elif isinstance(bit, int):
            self.length += 1
        else:
            raise ValueError("Invalid bit type")
        new_amps = np.zeros(2**len(self), dtype=np.complex128)
        for value in self.values:
            old_amp = self.amps[value.value]
            value.insert(bit, pos=pos)
            new_amps[value.value] = old_amp
        self.amps = new_amps

    def comparison_neg(self, N):
        for i in range(len(self.values)):
            cur_value = self.values[i].value
            if cur_value >= N:
                self.amps[cur_value] *= -1

    def check(self):
        for i in range(len(self.amps)):
            if self.amps[i] != 0 and BinaryInt[i, self.length] not in self.values:
                raise ValueError("Inconsistent values with amps")
            
    def controlled_add(self, 
                      pos_lst: List[int],
                      offsets: List[int]):
        visited = np.zeros(2**len(pos_lst))

        if 2**len(pos_lst) != len(offsets):
            raise ValueError("Didn't specify all offsets")
        for value in self.values:
            control_value = value[pos_lst]
            for i in range(offsets):
                offset = offsets[i]
                if control_value == i and visited[i] == 0:
                    self.values.remove(value)
                    new_value = value + offset
                    self.values.append(new_value)
                    cur_amp = self.amps[value.value]
                    self.amps[value.value] = 0
                    self.amps[new_value.value] = cur_amp
                    visited[i] = 1
        return 

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
    return Qint(values, amps, module, length)
