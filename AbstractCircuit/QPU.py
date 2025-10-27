from AbstractRegister import *
import numpy as np
from typing import List
from collections import defaultdict

class QPU():

    def __init__(self,
             registers = List[AbstractRegister]):
        """
        Allocate registers to the QPU
        """
        self.registers = registers

    def add_register(self,
                     added_registers: List[AbstractRegister],
                     circuit: "AbstractCircuit"):
        """
        Append the registers to the QPU

        Inputs:     The list of DataRegister to be added. The corresponding ancilla qubits
                    will also be automatically allocated to the QPU.
        """
        for register in added_registers:
            if register in self.registers:
                raise ValueError("register is already in the QPU")
            self.registers.append(register)
            if register.get_type() == "data":
                if register.pos in circuit.ancilla:
                    a = circuit.ancilla[register.pos]
                    self.registers.append(a)
    
    def count(self,
              double_count = False):
        """
        Count the number of gates in the QPU
        """
        count = defaultdict(int)
        registers = self.registers
        for register in registers:
            cur_count = register.count_gate(double_count = double_count)
            for key, value in cur_count.items():
                count[key] += value
        return count
    
    def count_connections(self):
        count = defaultdict(int)
        registers = self.registers
        print(registers)
        for register in registers:
            gates = register.gates
            for pos, gate in gates.items():
                if isinstance(gate, TwoQubitGate):
                    control = gate.control
                    target = gate.target
                    if control not in registers or target not in registers:
                        count[gate.type] += 1
        return count

    def count_T(self):
        count = 0
        registers = self.registers
        for register in registers:
            cur_count = register.count_T()
            count += cur_count
        return count

class QPUCluster():
    
    def __init__(self,
                 QPUs: List[QPU]):
        self.QPUs = QPUs


    
    