from QuantumGate import *
from typing import Dict
from collections import defaultdict

class AbstractRegister():
    def __init__(self,
                 pos: int,
                 gates: Dict[int, QuantumGate]):
        """
        Construct an abstract register class

        Inputs:
            pos: position of the register
            gates: all gates on the register. gates[gate position] = QuantumGate
                    gate position marks the depth position of the gate.
        """
        self.pos = pos
        self.gates = gates
        if gates == {}:
            depth = 0
        else:
            depth = max(gates.keys())
        self.depth = depth

    def __eq__(self,
               other):
        """
        If two registers have the same position and save type (data or ancilla), they are the same.
        I didn't check gate for simplicity
        """
        return (self.pos == other.pos) and (self.get_type() == other.get_type())
    
    def __in__(self,
               registers):
        found = False
        for register in registers:
            if self == registers:
                return True
        return found

    def append(self,
               depth: int,
               gate: QuantumGate):
        """
        Append a new gate to the circuit
        
        Inputs:
            depth:      the depth position of the gate
            gate:       the gate to be appended
        """
        self.gates[depth] = gate
        self.depth = depth + 1

    def add_single_qubit_gate(self,
                              type: str):

        cur_depth = self.depth
        gate = QuantumGate(type, self.pos)
        self.append(cur_depth, gate)

    def count_gate(self, double_count = True):
        """
        Count the number of gates on the register

        Inputs:
            double_count: If true, count the number of gates both from and to the register.
                        e.g. CNOT(i, j) is counted both in i-th register and j-th register.
                        If false, only count the number of gates from the register.
                        e.g. CNOT(i, j) is counted in i-th register but not j-th register.
                        The orgin of a Toffoli gate is defined as its first control qubit.
        
        Returns:
            count:      count[gate_type] = number of gates
        """
        count = defaultdict(int)
        for pos, gate in self.gates.items():
            if double_count:
                if isinstance(gate, CCGate):
                    gate_type = gate.gate.type
                    gate_type = "Ccontrol" + gate_type
                    count[gate_type] += 1
                else:
                    gate_type = gate.type
                    count[gate_type] += 1
            else:
                if isinstance(gate, TwoQubitGate):
                    gate_type = gate.type
                    control = gate.control
                    if self == control:
                        count[gate_type] += 1
                elif isinstance(gate, ToffoliGate):
                    gate_type = gate.type
                    control = gate.c1
                    if self == control:
                        count[gate_type] += 1
                elif isinstance(gate, CCGate):
                    control = gate.cc
                    gate_type = gate.gate.type
                    gate_type = "Ccontrol" + gate_type
                    if self == control:
                        count[gate_type] += 1
                else:
                    gate_type = gate.type
                    count[gate_type] += 1
            
        return count

    def count_T(self):
        """
        Count the number of T gates on the register

        Returns:
            count:  an int of number of T gates
        """
        count = 0
        for pos, gate in self.gates.items():
            if isinstance(gate, CCGate):
                cur_gate = gate.gate
                gate_type = cur_gate.type
            else:
                gate_type = gate.type
            if gate_type == "T" or gate_type == "Tdg":
                count += 1
        return count


    def X(self):
        self.add_single_qubit_gate("X")
    
    def H(self):
        self.add_single_qubit_gate("H")
    
    def Z(self):
        self.add_single_qubit_gate("Z")
    
    def MX(self):
        self.add_single_qubit_gate("MX")

    def MZ(self):
        self.add_single_qubit_gate("MZ")
    
    def T(self):
        self.add_single_qubit_gate("T")
    
    def Tdg(self):
        self.add_single_qubit_gate("Tdg")

    def Sdg(self):
        self.add_single_qubit_gate("Sdg")
    
    def S(self):
        self.add_single_qubit_gate("S")

    def get_type(self):
        """
        Get the type of the register. The support types are data/ancilla
        """
        if isinstance(self, DataRegister):
            return "data"
        elif isinstance(self, AncillaRegister):
            return "ancilla"
        else:
            raise ValueError("Invalid register type")
        
    def append_two_qubit_gate(self,
                              other,
                              type: str):
        """
        Add two qubit gates (CNOT/CZ)

        Inputs:
            other:      the target QuantumRegister
            type:       string of the type of the gate ("CZ" or "CNOT")
        """
        control_depth = self.depth
        target_depth = other.depth
        CNOT_depth = max([control_depth, target_depth])
        control_type = self.get_type()
        control = self
        target = other
        cur_gate = TwoQubitGate(type, self.pos, control, target)
        self.append(CNOT_depth, cur_gate)
        other.append(CNOT_depth, cur_gate)
    
    def CNOT(self, 
             other):
        self.append_two_qubit_gate(other, "CNOT")
    
    def appendCCgates(self,
                      gate: CCGate):
        """
        Append the classical controlled gate (CCGate). The origin of the gate is defined
        as the position of the classical signal.
        """
        cur_gate = gate
        targets = gate.targets
        cc = gate.cc
        cc_depth = cc.depth
        if gate.repeat:
            cc_depth -= 1
        max_depth = cc_depth
        for target in targets:
            max_depth = max([max_depth, target.depth])
        for target in targets:
            target.append(max_depth, cur_gate)
        if not gate.repeat:
            cc.append(max_depth, cur_gate)

    
    def CZ(self,
           other):
        self.append_two_qubit_gate(other, "CZ")
    
    def Toffoli(self,
                c2,
                target):
        c1_depth = self.depth
        c2_depth = c2.depth
        target_depth = target.depth
        Toffoli_depth = max([c1_depth, c2_depth, target_depth])
        cur_gate = ToffoliGate(self, c2, target)
        self.append(Toffoli_depth, cur_gate)
        c2.append(Toffoli_depth, cur_gate)
        target.append(Toffoli_depth, cur_gate)



class DataRegister(AbstractRegister):
    def __init__(self,
                 pos: int,
                 gates: Dict[int, QuantumGate]):
        super().__init__(pos, gates)

class AncillaRegister(AbstractRegister):
    def __init__(self,
                 pos: int,
                 gates: Dict[int, QuantumGate],
                 status: str):
        super().__init__(pos, gates)
        status_lst = ["idle", "busy"]
        if status not in status_lst:
            raise ValueError("Invalid status for ancilla registers")
        self.status = status
    
    def check_availablity(self):
        return self.status == "idle"
    
    def Clear(self):
        self.add_single_qubit_gate("Clear")
        self.status = "idle"