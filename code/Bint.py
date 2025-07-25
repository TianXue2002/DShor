import numpy as np
from typing import Union
from copy import copy
class BinaryInt:
    def __init__(self, value: int, length:int):
        self.length = length
        bin_str = bin(value)[2:].zfill(length)
        if not all(c in '01' for c in bin_str):
            raise ValueError("Must be binary digits")
        self.value = value
        self.binary = bin_str
    
    def __getitem__(self, pos):
        if isinstance(pos, int):
            new_binary = self.binary[(-1-pos)]
            new_value  = int(new_binary, 2)
            return BinaryInt(new_value, 1)
        elif isinstance(pos, slice):
            start = pos.start or 0
            stop = pos.stop or self.length
            step = pos.step or 1
            new_binary = ''.join(self.binary[-1 - i] for i in range(stop-1, start-1, -step))
            new_value  = int(new_binary, 2)
            return BinaryInt(new_value, stop - start)
        elif isinstance(pos, list) or isinstance(pos, np.ndarray):
            new_binary = ''.join(self.binary[-1-i] for i in reversed(pos))
            new_value  = int(new_binary, 2)
            return BinaryInt(new_value, len(pos))
        else:
            raise ValueError("Invalide index")
    def __str__(self):
        return self.binary
    
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, np.int64):
            result_value = (self.value + other) % (2**self.length)
            result_length = self.length
        elif isinstance(other, BinaryInt):
            result_value = (self.value + other.value) % (2**self.length)
            result_length = max([self.length, other.length])

        elif not isinstance(other, BinaryInt):
            raise ValueError("Cannot add a non BinaryInt to a BinaryInt")
        return BinaryInt(result_value, result_length)
    
    def __sub__(self, other):
        if isinstance(other, int):
            result_value = (self.value - other) % (2**self.length)
            result_length = self.length
        elif isinstance(other, BinaryInt):
            result_value = (self.value + other.value) % (2**self.length)
            result_length = max([self.length, other.length])

        elif not isinstance(other, BinaryInt):
            raise ValueError("Cannot add a non BinaryInt to a BinaryInt")
        return BinaryInt(result_value, result_length)
    
    def __lshift__(self, offset:int):
        value = self.value<<offset
        length = self.length + offset
        return BinaryInt(value, length)

    def __rshift__(self, offset:int):
        value = self.value>>offset
        length = self.length - offset
        return BinaryInt(value, length)
    
    def __mod__(self, module):
        value = self.value % module
        return BinaryInt(value, self.length)

    def __len__(self):
        return self.length
    
    def __eq__(self,
               other):
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, BinaryInt):
            return self.value == other.value
        else:
            raise ValueError("Invalid data type to compred with BinaryInt")

    def copy(self):
        return BinaryInt(self.value, self.length)
    
    def insert(self,
               bit:Union[int, str],
               pos = 0):
        
        if isinstance(bit, int):
            new_length = self.length + 1
            if bit > 1:
                raise ValueError("use string bit to insert more than 1 bit")
        elif isinstance(bit, str):
            new_length = self.length + len(bit)
        else:
            raise ValueError("Invalid bit type")
        new_bin_str = self.binary[:len(self)-pos] + str(bit) + self.binary[len(self)-pos:len(self)]
        new_value = int(new_bin_str, 2)
        
        self.length = new_length
        self.binary = new_bin_str
        self.value = new_value
        return


def modular_add(a: BinaryInt, 
                b: Union[BinaryInt, int], 
                N: int)-> BinaryInt:
    if not isinstance(a, BinaryInt):
        raise ValueError("The first integer must be BinaryInt")
    return (a+b) % N