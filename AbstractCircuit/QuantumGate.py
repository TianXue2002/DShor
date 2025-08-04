import numpy as np
from typing import Tuple, List

class QuantumGate():
    def __init__(self,
                 type: str,
                 position: int,):
        # All quantum gates supported by the current circuit
        gate_lst = ["X", "Y", "Z", "H", "S", "Sdg", "MX", "MY", "MZ", "CNOT", "CZ", 
                    "T", "Tdg", "Toffoli", "Clear"]
        if type not in gate_lst:
            raise ValueError("Unsupported gate type")
        self.type = type
        self.position = position

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