import numpy as np

class BinaryInt:
    def __init__(self, value: int, module: int, length:int):
        self.length = length
        self.module = module
        bin_str = bin(value)[2:].zfill(length)
        if not all(c in '01' for c in bin_str):
            raise ValueError("Must be binary digits")
        self.value = value
        self.binary = bin_str
        if self.value >= self.module:
            raise ValueError("Unmodularized value")

    def __getitem__(self, pos):
        return self.binary[(-1-pos)]
    
    def __str__(self):
        return (self.binary)
    
    def __add__(self, other):
        if isinstance(other, int):
            result_value = (self.value + other) % self.module
            result_length = self.length
        elif isinstance(other, BinaryInt):
            if self.module != other.module:
                raise ValueError("Cannot add two number with different modules")
            result_value = (self.value + other.value) % self.module
            result_length = max([self.length, other.length])

        elif not isinstance(other, BinaryInt):
            raise ValueError("Cannot add a non BinaryInt to a BinaryInt")
        return BinaryInt(result_value, self.module, result_length)
    
    def __lshift__(self, offset:int):
        value = self.value<<offset
        length = self.length + offset
        return BinaryInt(value, self.module, length)

    def __rshift__(self, offset:int):
        value = self.value>>offset
        length = self.length - offset
        return BinaryInt(value, self.module, length)
    
    # def __mod__(self, module):
    #     value = self.value % module
    #     return BinaryInt(value, self.length)