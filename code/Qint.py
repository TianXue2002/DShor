import numpy as np
from Bint import BinaryInt
from typing import List, Tuple, Callable, Union
import warnings
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
    
    def __add__(self, 
                other: int):
        qr = self.copy()
        result_amp = np.zeros(2**len(self), np.complex128)
        qr.amps = result_amp
        for i in range(len(self.values)):
            cur_value = self.values[i]
            updated_value = cur_value + other
            qr.values[i] = updated_value
            qr.amps[updated_value.value] = self.amps[cur_value.value]
        return qr
    

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
               pos = 0,
               basis = "Z"):
        if isinstance(bit, str):
            if len(bit) != 1:
                self.length += len(bit)
        elif isinstance(bit, int):
            self.length += 1
        else:
            raise ValueError("Invalid bit type")
        new_amps = np.zeros(2**len(self), dtype=np.complex128)
        if basis == "Z":
            for value in self.values:
                old_amp = self.amps[value.value]
                value.insert(bit, pos=pos)
                new_amps[value.value] = old_amp
        elif basis == "X":
            if isinstance(bit, str) and len(bit) > 1:
                bit_lst = list(bit)
                for cur_bit in bit_lst:
                    self.insert(cur_bit, pos, basis="X")
            else:
                new_values = self.values.copy()
                for value in self.values:
                    old_amp = self.amps[value.value]
                    new_value = value.copy()
                    value.insert(0, pos=pos)
                    new_value.insert(1, pos = pos)
                    new_values.append(new_value)
                    new_amps[value.value] = old_amp/np.sqrt(2)
                    new_amps[new_value.value] = (-1)**int(bit) * old_amp/np.sqrt(2)
                self.amps = new_amps
                self.values = new_values

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
                      offsets: List[int],
                      target: List[int]):
        if len(offsets) > 2**len(target):
            warnings.warn("The target size is smaller than the offset size")
        pos_lst.sort()
        visited = np.zeros(2**len(pos_lst))
        if 2**len(pos_lst) != len(offsets):
            raise ValueError("Didn't specify all offsets")
        if min(target) < max(pos_lst):
            controlled_lower = True
            module = 2**(np.max(target)+1)
        elif min(target) > max(pos_lst):
            controlled_lower = False
            module = 2**(np.min(target))
        elif min(target) == max(pos_lst):
            raise ValueError("target and control cannot overlap")
        new_values = self.values.copy()
        result_amps = np.zeros(2**(self.length), dtype=np.complex128)
        for value in self.values:
            control_value = value[pos_lst]
            for i in range(len(offsets)):
                offset = offsets[i]
                if control_value == i:
                    new_values.remove(value)
                    if controlled_lower:
                        new_value = (value + offset * 2**min(target)) % module + ((value.value)//module*module)
                    else:
                        upper_half = (value[target] + offset) % 2**(len(target))
                        lower_half = value.value % 2**(self.length - len(target))
                        new_value = 2**min(target) * upper_half.value + lower_half
                        new_value = BinaryInt(new_value, self.length)
                        # print("==")
                        # print(control_value, "control")
                        # print(value, "value")
                        # print(offset, "off")
                        # print(new_value, "new")
                                                
                    # print(control_value, "control")
                    # print(new_value, "new")
                    # print(value, "old")
                    # print((offset * 2**min(target)) % module, "add")
                    # print(offset, "offset")
                    # print(module, "module")
                    # print("===")
                    new_values.append(new_value)
                    cur_amp = self.amps[value.value]
                    result_amps[new_value.value] = cur_amp
                    visited[i] = 1
        self.amps = result_amps
        self.values = new_values
        return 
    
    def update_value(self,
                     original: Union[int,BinaryInt],
                     updated: Union[int,BinaryInt]):
        if isinstance(original, BinaryInt):
            original_value = original
        else:
            original_value = BinaryInt(original, self.length)
        if isinstance(updated, BinaryInt):
            updated_value = updated
        else:
            updated_value = BinaryInt(updated, self.length)
        found = False
        for i in range(len(self.values)):
            cur_value = self.values[i]
            if cur_value == original_value:
                self.values[i] = updated_value
                found = True
                break
        if not found:
            raise ValueError("Didn't find the value to be updated")
        cur_amp = self.amps[original_value.value]
        self.amps[original_value.value] = 0
        self.amps[updated_value.value] = cur_amp
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
