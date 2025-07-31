import numpy as np
from QuantumGate import QuantumGate, TwoQubitGate, ToffoliGate, CCGate
from typing import Dict, List
import matplotlib.pyplot as plt
from random import random
from help_function import *

from AbstractRegister import DataRegister, AncillaRegister, AbstractRegister

def teleported_Toffoli(self,
        i: int, 
        j: int,
        k: int):
    
    idle_register_lst = self.allocate_ancillas(3)
    data = self.data

    d0 = data[i]
    d1 = data[j]
    d2 = data[k]
    a0,a1,a2 = idle_register_lst

    # Prepare CCZ state
    a2.H()
    a1.H()
    
    a2.Toffoli(a1, a0)
    a2.CNOT(d2)
    a1.CNOT(d1)

    # Teleport CCZ to state
    d0.H()
    d0.CNOT(a0)
    
    # Measure d0
    
    p = random()
    if p < 0.5:
        g1 = CCGate(QuantumGate("Z", a0.pos), d0, [a0], "X")
        d0.appendCCgates(g1)
        g2 = TwoQubitGate("CZ", a1.pos, (a1.pos, "ancilla"), (a2.pos, "ancilla"))
        g2 = CCGate(g2, d0, [a1, a2], "X", repeat=True)
        d0.appendCCgates(g2)
    else:
        d0.MX()

    # Measure d1

    p = random()
    if p < 0.5:
        g1 = CCGate(QuantumGate("X", a1.pos), d1, [a1], "Z")
        d1.appendCCgates(g1)
        g2 = TwoQubitGate("CNOT", a2.pos, (a2.pos, "ancilla"), (a0.pos, "ancilla"))
        g2 = CCGate(g2, d1, [a2, a0], "Z", repeat=True)
        d1.appendCCgates(g2)
    else:
        d1.MZ()

    # Measure d2
    p = random()
    if p < 0.5:
        g1 = CCGate(QuantumGate("X", a2.pos), d2, [a2], "Z")
        d2.appendCCgates(g1)
        g2 = TwoQubitGate("CNOT", a1.pos, (a1.pos, "ancilla"), (a0.pos, "ancilla"))
        g2 = CCGate(g2, d2, [a1, a0], "Z", repeat=True)
        d2.appendCCgates(g2)
    else:
        d2.MZ()
    a0.H()

    # Clear ancilla qubits
    a0.Clear()
    a1.Clear()
    a2.Clear()

def AND(self,
        qi:AbstractRegister,
        qj: AbstractRegister,
        truth_table = [False, False]):
    
    data = self.data
    idle_register_lst = self.allocate_ancillas(1, pos_lst=[qj.pos])
    a0 = idle_register_lst[0]
    d0 = qi
    d1 = qj


    if truth_table[0]:
        qi.X()
    if truth_table[1]:
        qj.X()

    a0.T()
    d0.CNOT(a0)
    a0.Tdg()
    d1.CNOT(a0)
    a0.T()
    d0.CNOT(a0)
    a0.Tdg()
    a0.H()
    a0.Sdg()

    if truth_table[0]:
        qi.X()
    if truth_table[1]:
        qj.X()

def unAND(self,
            qi: AbstractRegister,
            qj: AbstractRegister,
            a: AncillaRegister,
            truth_table = [False, False]):
    if not isinstance(a, AncillaRegister):
        raise ValueError("unAnd must be based on an ancilla qubit")

    
    threshold = 1

    p = random()
    if p < threshold:
        if truth_table[0]:
            qi.X()
        if truth_table[1]:
            qj.X()

        g = TwoQubitGate("CZ", qi.pos, (qi.pos, qi.get_type()), (qj.pos, qj.get_type()))
        g = CCGate(g, a, [qi, qj], "X")
        a.appendCCgates(g)

        if truth_table[0]:
            qi.X()
        if truth_table[1]:
            qj.X()
    else:
        a.MX()
    a.Clear()
    
def multiAND(self,
                controls: List[AbstractRegister],
                truth_table: Dict[int, bool]):
    for i in range(len(controls) - 1):
        cur_table = [truth_table[i], truth_table[i+1]]
        qi = controls[i]
        qj = controls[i+1]
        self.AND(qi, qj, truth_table=cur_table)
        

def multiUnAND(self,
                controls: List[AbstractRegister],
                truth_table: Dict[int, bool]):
    for i in range(len(controls) - 1, 0, -1):
        cur_table = [truth_table[i-1], truth_table[i]]
        qi = controls[i-1]
        qj = controls[i]
        a = self.ancilla[i]
        self.unAND(qi, qj, a, cur_table)

def lookup(self,
            table:Dict[int, int],
            control_qubit:List[AbstractRegister],
            target_qubits: List[AbstractRegister]):
    
    L = len(control_qubit)
    for value in table:
        if value >= 2**L:
            raise ValueError("The loaded number is longer than the registers")
    table = table.copy()
    table = dict(sorted(table.items()))
    
    for i in range(len(table.keys())):
        key = list(table.keys())[i]
        cur_value = table[key]
        targets = num2controls(cur_value, L)
        controls = num2controls(key, L)
        if i == 0:
            msb_diff = L - 1
        else:
            pre_bin = format(prev_key, f'0{L}b')
            cur_bin = format(key, f'0{L}b')
            msb_diff = find_greatest_diff_bit(pre_bin, cur_bin)
            for j in range(msb_diff):
                if j < len(control_qubit) - 2:
                    qi = self.ancilla[control_qubit[j + 1].pos]
                else:
                    qi = self.data[control_qubit[j + 1].pos]
                qj = self.data[control_qubit[j].pos]
                a = self.ancilla[control_qubit[j].pos]
                truth_table = [True, controls[j]]
                self.unAND(qi, qj, a)
            if msb_diff == len(controls) - 2:
                qc = self.data[control_qubit[msb_diff + 1].pos]
                target_qubit = self.ancilla[control_qubit[msb_diff].pos]
                qc.CNOT(target_qubit)                    
            elif msb_diff < len(controls) - 2:
                qc = self.ancilla[control_qubit[msb_diff + 1].pos]
                target_qubit = self.ancilla[control_qubit[msb_diff].pos]
                qc.CNOT(target_qubit)                    
            
            

        for j in range(msb_diff - 1 , -1, -1):
            if j == L-2:
                qi = control_qubit[j+1]
                qj = control_qubit[j]
                truth_table = [controls[j+1], controls[j]]
                self.AND(qi, qj, truth_table=truth_table)
            else:
                prev_qubit = control_qubit[j + 1]
                qi = self.ancilla[prev_qubit.pos]
                qj = control_qubit[j]
                truth_table = [True, controls[j]]
                self.AND(qi, qj, truth_table=truth_table)
        for k in range(len(targets)):
            if targets[k] == False:
                cur_ancilla = self.ancilla[qj.pos]
                cur_ancilla.CNOT(target_qubits[k])
        prev_key = key

    for j in range(len(controls) - 1):
        if j < len(control_qubit) - 2:
            qi = self.ancilla[control_qubit[j + 1].pos]
        else:
            qi = self.data[control_qubit[j + 1].pos]
        qj = self.data[control_qubit[j].pos]
        a = self.ancilla[control_qubit[j].pos]
        truth_table = [True, controls[j]]
        self.unAND(qi, qj, a)

def add(self,
        q1_lst: List[AbstractRegister],
        q2_lst: List[AbstractRegister]):
    """
        q1_lst: list of quantum registers with classically loaded number
        q2_lst: list of working registers
    """
    add_len = min(len(q1_lst), len(q2_lst))
    for i in range(add_len - 1):
        q1 = q1_lst[i]
        q2 = q2_lst[i]
        q1n = q1_lst[i+1]
        q2n = q2_lst[i+1]
        if i == 0:
            self.AND(q1, q2)
            cur_overflow = self.ancilla[q2_lst[i].pos]
        else:
            self.AND(q1, q2)
            cur_overflow = self.ancilla[q2_lst[i].pos]
            prev_overflow = self.ancilla[q2_lst[i-1].pos]
            prev_overflow.CNOT(cur_overflow)
        if i != add_len - 2:
            cur_overflow.CNOT(q1n)
            cur_overflow.CNOT(q2n)
    
    q1 = q1_lst[add_len - 2]
    q2 = q2_lst[add_len - 2]
    q1n = q2_lst[add_len - 1]
    q2n = q2_lst[add_len - 1]
    overflow = self.ancilla[q2.pos]
    overflow.CNOT(q2n)

    for i in range(add_len - 2, -1, -1):
        q1 = q1_lst[i]
        q2 = q2_lst[i]
        if i != 0:
            q1p = q1_lst[i-1]
            q2p = q2_lst[i-1]
            cur_overflow = self.ancilla[q2.pos]
            previous_overflow = self.ancilla[q2p.pos]
            previous_overflow.CNOT(cur_overflow)
        a = self.ancilla[q2.pos]
        self.unAND(q1,q2,a)

    for i in range(add_len):
        q1 = q1_lst[i]
        q2 = q2_lst[i]
        q1.CNOT(q2)