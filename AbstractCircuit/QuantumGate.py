import numpy as np
from typing import Tuple, List, Dict
import copy

class QuantumGate():
    def __init__(self,
                 type: str,
                 position: int,):
        # All quantum gates supported by the current circuit
        gate_lst = ["X", "Y", "Z", "H", "S", "Sdg", "MX", "MY", "MZ", "CNOT", "CZ", 
                    "T", "Tdg", "Toffoli", "Clear", "Logical"]
        if type not in gate_lst:
            raise ValueError("Unsupported gate type")
        self.type = type
        self.position = position
    
    def copy(self):
        cls = self.__class__
        new_obj = cls.__new__(cls)
        for k, v in self.__dict__.items():
            if isinstance(v, (list, dict, set)):
                setattr(new_obj, k, v.copy())     # shallow copy containers
            else:
                setattr(new_obj, k, v)            # immutables: copy reference
        return new_obj

class TwoQubitGate(QuantumGate):
    def __init__(self, 
                 type: str, 
                 position: int,
                 control, 
                 target):
        super().__init__(type, position)
        type_lst = ["CNOT", "CZ"]
        if type not in type_lst:
            raise ValueError("Unsupported two qubit gate")
        if control == target:
            raise ValueError("Target and control must be different")
        self.control = control
        self.target = target

class ToffoliGate(QuantumGate):
    def __init__(self,
                c1,
                c2,
                target):
        type = "Toffoli"
        super().__init__(type, c1)
        self.c1 = c1
        self.c2 = c2
        self.target = target

class CCGate:
    def __init__(self,
                 gate: QuantumGate,
                 cc,
                 targets,
                 basis: str,
                 repeat = False):
        """
        The classical controlled gate

        Inputs:
            gate:   The quantum gate to be classical controlled. e.g. a classical controlled CNOT
                    has gate of a CNOT
            cc:     The register gives the classical signal
            targets: The target qubits
            basis:  The measurement basis of the signa; (X/Z)
            repeat: If more than one gates are controlled by the same signal, all gates except
                    the first gate should have repeat = True. 
        """
        self.gate = gate
        self.cc = cc
        self.basis = basis
        self.targets = targets
        self.repeat = repeat

class LogicalGate(QuantumGate):
    def __init__(self,
                qi: "AbstractRegister",
                qj: "AbstractRegister",
                a: "AncillaRegister",
                truth_table: List[bool],
                type: str):
        if type not in ["AND", "UNAND"]:
            raise ValueError("Invalid Logical Gate")
        super().__init__("Logical", qi.pos)
        self.qi = qi
        self.qj = qj
        self.a = a
        self.truth_table = truth_table
        self.type = type

class LookupGate(QuantumGate):
    def __init__(self,
                target:List[bool],
                control_qubit:List["AbstractRegister"],
                target_qubits: List["AbstractRegister"],
                QPU_assignment = None,
                antena_assignment = None,
                antena_ancilla = None):
        super().__init__("Logical", control_qubit.pos)
        self.target = target
        self.control = control_qubit
        self.target_qubits = target_qubits
        self.QPU_assignment = QPU_assignment
        self.antena_assignment = antena_assignment
        self.antena_ancilla = antena_ancilla

class GHZprep(QuantumGate):
    def __init__(self, 
                antena_ancilla: List["AbstractRegister"],
                antena_assignment: List["AbstractRegister"]):
        type = "Logical"
        super().__init__(type, antena_assignment[0][0].pos)
        self.antena_ancilla = antena_ancilla
        self.antena_assignment = antena_assignment