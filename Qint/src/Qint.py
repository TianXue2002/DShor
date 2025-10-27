import numpy as np
from Base import Base
from typing import TYPE_CHECKING
from LookupTable import *
from toolkit import *
import random
from typing import Iterable


class Qint(Base):
    def __init__(self, 
                parent: Base,
                start: int,
                length: int,
                overflow = False):
        self.data = parent.data
        self._parent = parent
        self.id = id(self)
        self.start = start
        self.length = length
        self.overflow = overflow
    
    def end(self):
        return self.start + len(self) - 1

    def __len__(self):
        return self.length - (self.overflow == True)
    
    def __str__(self):
        lines = []
        for value, amp in self._parent.data.items():
            # Convert to binary, padded to full width
            s = f"{value:0{self._parent.num_qubits}b}"

            # Compute indices from the right (LSB = index 0)
            start_from_right = self._parent.num_qubits - (self.start + self.length)
            end_from_right = self._parent.num_qubits - self.start

            output = (
                s[:start_from_right]
                + "|"
                + s[start_from_right:end_from_right]
                + "|"
                + s[end_from_right:]
            )
            lines.append(f"{output} has amp {amp}")
        return "\n".join(lines)


    def __getitem__(self, key):
        parent = self._parent
        if isinstance(key, int):
            return Qint(parent, self.start + key, 1, overflow = self.overflow)
        elif isinstance(key, slice):
            start = key.start or 0
            stop = key.stop or len(self)
            stop = stop + (self.overflow == True)
            return Qint(parent, self.start + start, stop - start, overflow = self.overflow)
        else:
            raise TypeError("Invalid index type for Qint")

    
    def __iadd__(self, offset):
        num_qubit = self._parent.num_qubits
        new_data = {}
        if isinstance(offset, LookupTable):
            Q_add = offset.address
            table = offset.table
            start = Q_add.start
            end = Q_add.start + Q_add.length - 1
            for value, amp in self.data.items():
                qubit_start = self.start
                cur_address = extract_bits(value, start, end)
                # print(cur_address, "add")
                cur_offset = table[cur_address]
                # print(f"{value:0{self._parent.num_qubits}b}","initial")
                cur_value = extract_bits(value, self.start, self.start + len(self) - 1 + self.overflow)
                cur_value = (cur_value + cur_offset) % (2**(len(self) + (self.overflow == True)))
                cur_value = modify_bits(value, qubit_start, len(self)+ (self.overflow == True), cur_value)
                if cur_value in new_data.keys():
                    raise ValueError("Dulplicate values in the qint")
                new_data[cur_value] = amp
        elif isinstance(offset, int):
            for value, amp in self.data.items():
                qubit_start = self.start
                cur_value = extract_bits(value, self.start, self.start + len(self) - 1 + self.overflow)
                cur_value = (cur_value + offset) % (2**(len(self) + (self.overflow == True)))
                cur_value = modify_bits(value, qubit_start, len(self) + (self.overflow == True), cur_value)
                if cur_value in new_data.keys():
                    raise ValueError("Dulplicate values in the qint")
                new_data[cur_value] = amp
        if len(new_data.keys()) != len(self.data.keys()):
            raise ValueError("Inconsistent value before and after addition")
        self._parent.data = new_data
        for qubit in self._parent.qubits.values():
            qubit.data = new_data
        return self
    
    def __isub__(self, offset):
        n = len(self)
        if isinstance(offset, int):
            offset = (-offset) % (2**(n+self.overflow))
        elif isinstance(offset, LookupTable):
            table = offset.table
            for i in table.keys():
                cur_value = table[i]
                table[i] = (-cur_value) % (2**(n+self.overflow))
        return self.__iadd__(offset)

    def __ixor__(self, control:"Qint"):
        data = self.data
        new_data = {}
        if len(self) < len(control):
            raise ValueError("control qubit must be shorter than or equal to the target qubit")
        for value, amp in data.items():
            control_bit = extract_bits(value, control.start, self.end())
            target_bit = extract_bits(value, self.start, self.end())
            new_target = target_bit ^ control_bit
            new_value = modify_bits(value, self.start, self.end(), new_target)
            new_data[new_value] = amp
        self._parent.data = new_data
        return self

    def remove(self,
               index:Iterable[int]):
        new_data = {}
        if isinstance(index, int):
            index = list(index)
        index = np.array(index)
        index = index + self.start
        for value, amp in self._parent.data.items():
            new_value = remove_bits_from_int(value, index)
            # print(f"{value:0{21}b}", "old")
            # print(f"{new_value:0{16}b}", "new")
            new_data[new_value] = amp
        self._parent.data = new_data
        self.length = len(self) - len(index)
        self._parent.num_qubits -= len(index)

    def mx_rz(self):
        """
        Unphysically set the measurement result as a random bit string of length n
        """
        n = len(self)
        start = self.start
        address_length = self._parent.address_length
        measurement = random.getrandbits(len(self))
        # update the wave functions
        new_data = {}
        for value, amp in self._parent.data.items():
            current_value = extract_bits(value, start, start+len(self) - 1)
            phase = (measurement & current_value).bit_count()
            measured_bit = modify_bits(value, start, len(self), 0)
            new_data[measured_bit] = (self._parent.data[value] + phase%2) % 2
        self._parent.data = new_data
        return measurement
    
    def zgeq(self, offset):
        for value, amp in self._parent.data.items():
            if value > offset:
                print(self._parent.data[value], "test")
                self._parent.data[value] == ~self._parent.data[value]
    
    def phase_up(self, table, Q_add):
        """
        Unphysically set the measurement result as a random bit string of length n
        """
        n = len(self)
        start = self.start
        address_length = self._parent.address_length
        measurement = random.getrandbits(len(self))
        # update the wave functions
        for value, amp in self._parent.data.items():
            current_value = extract_bits(value, start, start+len(self) - 1)
            phase = (measurement ^ current_value).bit_count()
            self._parent.data[value] = (self._parent.data[value] + phase%2) % 2
        
        # record the phaseup table
        for i in range(2**address_length):
            start_bit = self.start - Q_add.start
            print(Q_add.start, self.start)
            print(start_bit, "start")
            measured_bits = extract_bits(i, start_bit, len(self))
            target = table[measured_bits]            
            phase =  (measurement ^ target).bit_count()
            self._parent.phase_up[i] = (self._parent.phase_up[address] + phase%2) % 2
