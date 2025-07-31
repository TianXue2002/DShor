import numpy as np
from QuantumGate import QuantumGate, TwoQubitGate, ToffoliGate, CCGate
from typing import Dict, List
import matplotlib.pyplot as plt
from random import random
from help_function import *
from FundamentalOperations import *

from AbstractRegister import DataRegister, AncillaRegister, AbstractRegister

class AbstractCircuit():
    def __init__(self,
                 length: int,
                 data_registers: Dict[int, DataRegister],
                 ancilla_registers: Dict[int, AncillaRegister]):

        self.length = length
        self.data = data_registers
        self.ancilla = ancilla_registers
        if length != len(data_registers.keys()) + len(ancilla_registers.keys()):
            raise ValueError("Inconsistent length")

    def __len__(self):
        if self.length != len(self.data.keys()) + len(self.ancilla.keys()):
            raise ValueError("Inconsistent length")
        return self.length
    
    def __getitem__(self,
                    index):
        if isinstance(index, int):
            return self.data[index]
        elif isinstance(index, list):
            result = []
            for i in index:
                result.append(self.data[i])
            return result
        elif isinstance(index, slice):
            start = index.start or 0
            stop = index.stop or len(self)
            step = index.step or 1
            result = []
            for i in range(start, stop, step):
                result.append(self.data[i])
            return result
        else:
            raise ValueError("Unsupport key for slice")
    
    def drawTwoQubitGate(self,
                         reg: AbstractRegister,
                         gate: QuantumGate,
                         x: int,
                         ax,
                         cc = False):
        gate_color = "black"
        if cc:
            gate_color = "blue"

        control = gate.control
        target = gate.target

        y = 2*reg.pos + (reg.get_type() == "ancilla")
        control_pos = control.pos
        control_type = control.get_type()
        if control_type == "data":
            y_ref = 2*control_pos
        else:
            y_ref = 2*control_pos + 1
        if y != y_ref:
            return
        # Two-qubit gate
        pos = reg.pos
        
        # control_type = control[1]
        # target_type = target[1]
        # if control_type == "data":
        #     y_control = 2*control[0]
        # else:
        #     y_control = 2*control[0] + 1

        
        y_control = 2*control.pos + (control.get_type() == "ancilla")
        target_type = target.get_type()
        
        y_target = 2*target.pos + (target_type == "ancilla")

        ax.plot([x, x], [y_control, y_target], 'k-', linewidth=1, color = gate_color)
        ax.plot(x, y_control, 'ko', markersize=6, color = gate_color)
        if gate.type == "CNOT":
            circle = plt.Circle((x, y_target), 0.2, fill=False, edgecolor=gate_color, linewidth=1.5)
            ax.add_patch(circle)
            ax.plot([x, x], [y_target - 0.2, y_target + 0.2], 'k-', linewidth=1, color = gate_color)
            ax.plot([x - 0.2, x + 0.2], [y_target, y_target], 'k-', linewidth=1, color = gate_color)
        elif gate.type == "CZ":
            ax.plot(x, y_target, 'ko', markersize=6, color = gate_color)
    
    def drawToffoli(self,
                    reg: AbstractRegister,
                    gate: QuantumGate,
                    x: int,
                    ax):
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        y_ref = 2*gate.c1[0] + (gate.c1[1] == "ancilla")
        if y != y_ref:
            return
        c1 = 2*gate.c1[0] + (gate.c1[1] == "ancilla")
        c2 = 2*gate.c2[0] + (gate.c2[1] == "ancilla")
        target = 2*gate.target[0] + (gate.target[1] == "ancilla")
        ax.plot([x, x], [max([c1,c2]), target], 'k-', linewidth=1)
        ax.plot(x, c1, 'ko', markersize=6)
        ax.plot(x, c2, 'ko', markersize=6)
        circle = plt.Circle((x, target), 0.2, fill=False, edgecolor='black', linewidth=1.5)
        ax.add_patch(circle)
        ax.plot([x, x], [target - 0.2, target + 0.2], 'k-', linewidth=1)
        ax.plot([x - 0.2, x + 0.2], [target, target], 'k-', linewidth=1)

    def drawSingleGate(self,
                    reg: AbstractRegister,
                    gate: QuantumGate,
                    x: int,
                    ax,
                    cc = False):
        # Single-qubit gate
        patch_color = "lightblue"
        if cc:
            patch_color = "blue"
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        ax.add_patch(plt.Rectangle((x - 0.2, y - 0.2), 0.4, 0.4,
                                fill=True, color=patch_color, edgecolor='black'))
        ax.text(x, y, gate.type, ha='center', va='center', fontsize=8)
    
    def drawCCGate(self,
                    reg: AbstractRegister,
                    gate: CCGate,
                    x: int,
                    ax,):
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        cc = gate.cc
        cur_gate = gate.gate
        targets = gate.targets
        y_ref = 2*cc.pos + (cc.get_type() == "ancilla")
        basis = gate.basis
        if y != y_ref and not gate.repeat:
            return
        if gate.repeat:
            y_ref = 2*targets[0].pos + (targets[0].get_type()=="ancilla")
            if y != y_ref:
                return
            
        if not gate.repeat:
            if basis == "X":
                Mgate = QuantumGate("MX", cc.pos)
            if basis == "Z":
                Mgate = QuantumGate("MZ", cc.pos)
            self.drawSingleGate(reg, Mgate, x, ax, cc=True)
        offset = 0.03  # horizontal spacing between the two lines
        
        if isinstance(cur_gate, TwoQubitGate):
            control = cur_gate.control
            target = cur_gate.target
            y1 = 2*control.pos + (control.get_type() == "ancilla")
            y2 = 2*target.pos + (target.get_type() == "ancilla")
            y_target = min([y1, y2])
            if not gate.repeat:
                ax.plot([x - offset, x - offset], [y+0.2, y_target], linestyle='-', color='black', linewidth=1)
                ax.plot([x + offset, x + offset], [y+0.2, y_target], linestyle='-', color='black', linewidth=1)
            self.drawTwoQubitGate(gate.targets[0], cur_gate, x, ax, cc=True)
        else:
            target = gate.targets[0]
            y_target = 2*target.pos + (target.get_type() == "ancilla")
            if not gate.repeat:
                ax.plot([x - offset, x - offset], [y+0.2, y_target-0.2], linestyle='-', color='black', linewidth=1)
                ax.plot([x + offset, x + offset], [y+0.2, y_target-0.2], linestyle='-', color='black', linewidth=1)
            self.drawSingleGate(gate.targets[0], cur_gate, x, ax, cc=True)
        
    def draw_circuit(self):

        all_registers = list(self.data.values()) + list(self.ancilla.values())
        num_qubits = 2*len(self.data) + 1
        max_depth = max([register.depth for register in all_registers], default=0)
        
        fig, ax = plt.subplots(figsize=(max([6, max_depth]), max([3, num_qubits])))

        # Draw horizontal lines for each qubit
        for pos, data_register in self.data.items():
            ax.hlines(y=2*pos, xmin=0, xmax=max_depth+1, color='black', linewidth=0.5)
            ax.text(-0.5, 2*pos, f'q{pos}', fontsize=12, ha='right', va='center')
        
        for pos, ancilla_register in self.ancilla.items():
            ax.hlines(y=2*pos+1, xmin=0, xmax=max_depth+1, color='red', linewidth=0.5)
            ax.text(-0.5, 2*pos+1, f'a{pos}', fontsize=12, ha='right', va='center')

        # Draw gates
        for reg in all_registers:
            for depth, gate in reg.gates.items():
                x = depth + 0.5
                if reg.get_type() == "ancilla":
                    y = 2 * reg.pos + 1
                else:
                    y = 2*reg.pos
                if isinstance(gate, TwoQubitGate):
                    self.drawTwoQubitGate(reg, gate, x, ax)
                elif isinstance(gate, ToffoliGate):
                    self.drawToffoli(reg, gate, x, ax)
                elif isinstance(gate, CCGate):
                    self.drawCCGate(reg, gate, x, ax)
                else:
                    self.drawSingleGate(reg, gate, x, ax)
                    
        ax.set_ylim(-1, num_qubits)
        ax.set_xlim(0, max_depth + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout()
        plt.show()


    def add_ancilla(self, pos = None):
        if pos == None:
            if len(self.ancilla.keys()) == 0:
                cur_pos = 0
            else:
                found = False
                for pos, ancilla in self.ancilla.items():
                    if ancilla.check_availablity():
                        cur_pos = pos
                        found = True
                        break
                if not found:
                    cur_pos = max([pos for pos in self.ancilla.keys()]) + 1
        else:
            if pos in self.ancilla.keys():
                if self.ancilla[pos].status == "busy":
                    raise ValueError("The current ancilla is busy")
                else:
                    cur_ancilla = self.ancilla[pos]
                    return cur_ancilla
            else:
                cur_pos = pos
        cur_ancilla = AncillaRegister(cur_pos, {}, "busy")
        self.ancilla[cur_pos] = cur_ancilla
        self.length += 1
        return cur_ancilla
    
    def add_data(self):
        if len(self.data.keys()) == 0:
            cur_pos = 0
        else:
            cur_pos = max(self.data.keys()) + 1
        cur_data = DataRegister(cur_pos, {})
        self.data[cur_pos] = cur_data
        self.length += 1
        return cur_data
    
    def allocate_ancillas(self,
                          num: int,
                          pos_lst = []):
        
        idle_register_lst = []
        # Allocate idle ancillas
        if pos_lst == []:
            for pos, register in self.ancilla.items():
                if register.check_availablity() and len(idle_register_lst) < num:
                    idle_register_lst.append(register)
            num_added_ancilla = num - len(idle_register_lst)
            for i in range(num_added_ancilla):
                added_ancilla = self.add_ancilla()
                idle_register_lst.append(added_ancilla)
        else:
            for i in range(num):
                added_ancilla = self.add_ancilla(pos = pos_lst[i])
                idle_register_lst.append(added_ancilla)

        for ancilla in idle_register_lst:
            ancilla.status = "busy"
        return idle_register_lst

AbstractCircuit.teleported_Toffoli = teleported_Toffoli
AbstractCircuit.AND = AND
AbstractCircuit.unAND = unAND
AbstractCircuit.multiAnd = multiAND
AbstractCircuit.lookup = lookup
AbstractCircuit.add = add