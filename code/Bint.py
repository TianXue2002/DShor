import numpy as np
from typing import Union

class BinaryInt:
    def __init__(self, value: int, length:int):
        self.length = length
        bin_str = bin(value)[2:].zfill(length)
        if not all(c in '01' for c in bin_str):
            raise ValueError("Must be binary digits")
        self.value = value
        self.binary = bin_str

    def __getitem__(self, pos):
        return self.binary[(-1-pos)]
    
    def __getitem__(self, pos):
        if isinstance(pos, int):
            new_binary = self.binary[(-1-pos)]
            new_value  = int(new_binary, 2)
            return BinaryInt(new_value, 1)
        elif isinstance(pos, slice):
            start = pos.start or 0
            stop = pos.stop
            step = pos.step or 1
            new_binary = ''.join(self.binary[-1 - i] for i in range(start-1, stop-1, step))
            new_value  = int(new_binary, 2)
            return BinaryInt(new_value, stop - start)
        else:
            raise ValueError("Invalide index")
    def __str__(self):
        return self.binary
    
    def __add__(self, other):
        if isinstance(other, int):
            result_value = (self.value + other)
            result_length = self.length
        elif isinstance(other, BinaryInt):
            result_value = (self.value + other.value)
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

def modular_add(a: BinaryInt, 
                b: Union[BinaryInt, int], 
                N: int)-> BinaryInt:
    if not isinstance(a, BinaryInt):
        raise ValueError("The first integer must be BinaryInt")
    return (a+b) % N