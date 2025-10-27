import numpy as np
from QuantumGate import QuantumGate, TwoQubitGate, ToffoliGate, CCGate
from typing import Dict, List
import matplotlib.pyplot as plt
from random import random
from help_function import *
from QPU import QPU

from AbstractRegister import DataRegister, AncillaRegister, AbstractRegister
from AbstractGate import raw_lookup

def ghz_preparation(antena_ancilla: List[AbstractRegister],
                    antena_assignment: List[AbstractRegister],
                    shift = 0):
    for i in range(len(antena_ancilla)):
        cur_antena = antena_assignment[i][shift]
        cur_ancilla = antena_ancilla[i][shift]
        cur_antena.H()
        cur_antena.CNOT(cur_ancilla)

    for i in range(len(antena_ancilla)):
        cur_ancilla = antena_ancilla[i][shift]
        antena_assignment[i+1][shift].CNOT(cur_ancilla)
    
    for i in range(len(antena_ancilla)):
        cur_ancilla = antena_ancilla[i][shift]
        if i == len(antena_ancilla) - 1:
            for k in range(len(antena_assignment)):
                cur_antena = antena_assignment[k][shift]
                g = QuantumGate("X", cur_antena.pos)
                repeat = True
                if k == len(antena_assignment) - 1:
                    repeat = False
                gate = CCGate(g, cur_ancilla, [cur_antena], basis="Z", repeat=repeat)
                cur_ancilla.appendCCgates(gate)
        else:
            cur_ancilla.MZ()
        

def modular_lookup(control_qubit:AbstractRegister,
                   target_qubits: List[AbstractRegister],
                   targets: List[bool],
                   QPU_assignment: List[AbstractRegister],
                   antena_assignment: List[AbstractRegister],
                   antena_ancilla: List[AbstractRegister],
                   decompose = False,
                   gate_cost = None,
                   shift = 0):
    if not decompose:
        raw_lookup(control_qubit, target_qubits, targets, QPU_assignment,
                   antena_assignment, antena_ancilla, gate_cost = gate_cost, shift = shift)
    else:
        ghz_preparation(antena_ancilla, antena_assignment, shift = shift)
        antena_00 = antena_assignment[0][-1]
        antena_assignment[0][shift].CNOT(antena_00)
        for i in range(1, len(QPU_assignment)):
            cur_registers = QPU_assignment[i]
            cur_antena = antena_assignment[i-1][shift]
            for k in range(len(targets)):
                if targets[k] == False and target_qubits[k] in cur_registers:
                    cur_antena.CNOT(target_qubits[k])

        max_depth = 0
        source_qubit = None

        for i in range(1, len(QPU_assignment)):
            signal = antena_assignment[i-1][shift]
            signal.MX()
            if signal.depth > max_depth:
                max_depth = signal.depth
                source_qubit = signal
            
        qubit = control_qubit
        g = QuantumGate("Z", qubit.pos)
        repeat = False
        gate = CCGate(g, source_qubit, [qubit], basis="X", repeat=repeat)
        qubit.appendCCgates(gate)

        control_qubit.CNOT(antena_00)
        
        for i in range(len(target_qubits)):
            qubit = target_qubits[i]
            g = QuantumGate("X", qubit.pos)
            repeat = True
            if i == 0:
                repeat = False
            gate = CCGate(g, antena_00, [qubit], basis="Z", repeat=repeat)
            qubit.appendCCgates(gate)
    return
        
