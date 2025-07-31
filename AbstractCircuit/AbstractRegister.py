from QuantumGate import *
from typing import Dict
from collections import defaultdict

class AbstractRegister():
    def __init__(self,
                 pos: int,
                 gates: Dict[int, QuantumGate]):
        self.pos = pos
        self.gates = gates
        if gates == {}:
            depth = 0
        else:
            depth = max(gates.keys())
        self.depth = depth

    def append(self,
               depth: int,
               gate: QuantumGate):
        self.gates[depth] = gate
        self.depth = depth + 1

    def add_single_qubit_gate(self,
                              type: str):
        cur_depth = self.depth
        gate = QuantumGate(type, self.pos)
        self.append(cur_depth, gate)

    def count_gate(self):
        count = defaultdict(int)
        for gate in self.gates:
            gate_type = gate.type
            if isinstance(gate, TwoQubitGate):
                control = TwoQubitGate.control


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
        if isinstance(self, DataRegister):
            return "data"
        elif isinstance(self, AncillaRegister):
            return "ancilla"
        else:
            raise ValueError("Invalid register type")
        
    def append_two_qubit_gate(self,
                              other,
                              type: str):
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
        cur_gate = ToffoliGate([self.pos, self.get_type()], [c2.pos, c2.get_type()], [target.pos, target.get_type()])
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