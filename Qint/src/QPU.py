import numpy as np
from Base import Base

class QPU(Base):
    def __init__(self):
        self.qubits = {}
        self.data = {0:0}
        self.num_qubits = 0
        self.phase_up = {}
        self.address_length = 0

    def allocate_qubits(self, length, type = "data"):
        from Qint import Qint
        data = {0:0}
        new_data = {}
        for value, amp in self.data.items():
            new_value = value << length
            new_data[new_value] = amp
        self.data =new_data
        for qubit in self.qubits.values():
            qubit.start += length
            qubit.data = new_data
            qubit.data = new_data
        self.num_qubits += length
        new_int = Qint(self, 0, length)
        self.qubits[new_int.id] = new_int
        if type == "address":
            for i in range(2**length):
                self.phase_up[i] = 0
        self.address_length += length
        return new_int