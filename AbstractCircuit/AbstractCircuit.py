import numpy as np
from QuantumGate import QuantumGate, TwoQubitGate, ToffoliGate, CCGate
from typing import Dict, List
import matplotlib.pyplot as plt
from random import random
from help_function import *
from FundamentalOperations import *
from collections import defaultdict

from AbstractRegister import DataRegister, AncillaRegister, AbstractRegister

class AbstractCircuit():
    def __init__(self,
                 length: int,
                 data_registers: Dict[int, DataRegister],
                 ancilla_registers: Dict[int, AncillaRegister]):
        """
        Inputs:
            length:             the number of the qubits in the circuit
            data_registers:     a diction data[qubit position] = DatRegister
            ancilla_registers:  a dictioon ancilla[qubit posiiton] = AncillaRegister
        """
        self.length = length
        self.data = data_registers
        self.ancilla = ancilla_registers
        # check number of qubits in the circuit
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
    
    def add_ancilla(self, pos = None):
        """
        By default, each ancilla is uniquely belonged to one data register. The ancilla qubits
        is atomatically marked as "busy". They will only be marked as "idle" when they are 
        measured (reset). This is only true for the modular exponentiation protocol. 
        It doesn't support more than one ancilla for one data qubit now.

        Inputs:
            pos: position of the ancilla qubit. If the argument is not given, append the ancilla qubits
            to the end of the circuit
        """
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
    
    def add_data(self, type, pos = None):
        """
        Append a data qubits at the end of the circuit.
        """
        if pos == None:
            if len(self.data.keys()) == 0:
                cur_pos = 0
            else:
                cur_pos = max(self.data.keys()) + 1
        else:
            if pos in self.data.keys():
                raise ValueError("This position already has a data")
            else:
                cur_pos = pos
        cur_data = DataRegister(cur_pos, {})
        cur_data.type = type
        self.data[cur_pos] = cur_data
        self.length += 1
        return cur_data
    
    def insert_data(self, type, pos):
        """
        Insert a data qubit register at pos and push all other qubits back by 1
        """
        new_data = {}
        for data_pos, register in self.data.items():
            if data_pos >= pos:
                new_data[data_pos + 1] = register
                register.pos += 1
            else:
                new_data[data_pos] = register
        cur_data = DataRegister(pos, {})
        cur_data.type = type
        new_data[pos] = cur_data
        self.data = new_data
    
    def allocate_ancillas(self,
                          num: int,
                          pos_lst = []):
        """
        Allocate more than one busy ancilla qubits.
        Inputs:
            num:        number of ancilla qubits
            pos_lst:    a lis of the postions of allocated ancilla qubits. If not position is give,
            it will allocate idle ancilla and add new ancilla qubits if needed.
        
        Returns:
            the idle ancilla qubits it allocates
        """
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
    
    def count_gate(self):
        """
        Count the number of gates

        Returns:
            count:      a diction of count[gate_type] = number of gates
        """
        count = defaultdict(int)
        for key in self.data.keys():
            register = self.data[key]
            cur_count = register.count_gate(double_count = False)
            for key, value in cur_count.items():
                count[key] += value
    
        for key in self.ancilla.keys():
            register = self.ancilla[key]
            cur_count = register.count_gate(double_count = False)
            for key, value in cur_count.items():
                count[key] += value
        return count

    def depth(self):
        max_depth = 0

        for qubit in self.data.values():
            if qubit.depth > max_depth:
                max_depth = qubit.depth
        
        for qubit in self.ancilla.values():
            if qubit.depth > max_depth:
                max_depth = qubit.depth
        
        return max_depth

    # Drawing function. They can be ignored
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
                    ax,):
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        qc1 = gate.c1
        qc2 = gate.c2
        qtarget = gate.target

        y_ref = 2*qc1.pos + (qc1.get_type() == "ancilla")
        if y != y_ref:
            return
        c1 = 2*qc1.pos + (qc1.get_type() == "ancilla")
        c2 = 2*qc2.pos + (qc2.get_type() == "ancilla")
        target = 2*qtarget.pos + (qtarget.get_type() == "ancilla")
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
                    cc = False,
                    if_text = False):
        # Single-qubit gate
        patch_color = "lightblue"
        if cc:
            patch_color = "blue"
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        ax.add_patch(plt.Rectangle((x, y - 0.2), 0.4, 0.4,
                                fill=True, color=patch_color, edgecolor='black'))
        if if_text:
            ax.text(x+0.2, y, gate.type, ha='center', va='center', fontsize=8)
    
    def drawCCGate(self,
                    reg: AbstractRegister,
                    gate: CCGate,
                    x: int,
                    ax,
                    if_text = False):
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
            self.drawSingleGate(reg, Mgate, x, ax, cc=True, if_text = if_text)
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
            self.drawSingleGate(gate.targets[0], cur_gate, x, ax, cc=True, if_text = if_text)

    def drawLogicalGate(self,
                        reg: AbstractRegister,
                        gate: QuantumGate,
                        x: int,
                        ax,
                        if_text = False):
        patch_color = "lightblue"
        if reg != gate.qi:
            return
        qi = gate.qi
        qj = gate.qj
        a = gate.a
        yi = 2*qi.pos + (qi.get_type()=="ancilla")
        yj = 2*qj.pos + (qj.get_type()=="ancilla")
        ya = 2*a.pos + (a.get_type()=="ancilla")
        y0 = min([yi, yj, ya])
        y1 = max([yi, yj, ya])
        depth = gate.depth
        ax.add_patch(plt.Rectangle((depth, y0 - 0.2), gate.length - 1.4, 0.4+y1-y0,
                                fill=True, color=patch_color, edgecolor='black'))
        if if_text:
            ax.text(depth+(gate.length-1.4)/2, (y0 + y1)/2, gate.type, ha='center', va='center', fontsize=15)

    def drawGHZprep(self,
                reg: AbstractRegister,
                gate: QuantumGate,
                x: int,
                ax,
                if_text = False):
        
        antena_ancilla = gate.antena_ancilla
        antena_assignment = gate.antena_assignment
        depth = gate.depth
        length = gate.length
        pos_lst = []
        for qubit_lst in antena_ancilla.values():
            for qubit in qubit_lst:
                cur_pos = 2*qubit.pos + (qubit.get_type()=="ancilla")
                pos_lst.append(cur_pos)
        
        for qubit_lst in antena_assignment.values():
            for qubit in qubit_lst:
                cur_pos = 2*qubit.pos + (qubit.get_type()=="ancilla")
                pos_lst.append(cur_pos)
        
        y0 = min(pos_lst)
        y1 = max(pos_lst)
        x0 = depth
        x1 = depth + length

        patch_color = "red"
        ax.add_patch(plt.Rectangle((x0 - 0.2, y0 - 0.2), length, 0.4+y1-y0,
                                fill=True, color="red", edgecolor='black'))
        if if_text:
            ax.text((x0-0.2+length/2), (y0 + y1)/2, "GHZ Prep", ha='center', va='center', fontsize=15)

    def draw_circuit(self, if_text = False, if_line = False):

        all_registers = list(self.data.values()) + list(self.ancilla.values())
        num_qubits = 2*len(self.data) + 1
        max_depth = max([register.depth for register in all_registers], default=0)
        
        fig, ax = plt.subplots(figsize=(min([300, max_depth]), min([100, num_qubits])))
        plt.rcParams["figure.dpi"] = 150   # default is usually 100+ or 150
        name_count = defaultdict(int)
        # c_count = 0
        # t_count = 0
        # w_count = 0
        # antena_count = 0
        if if_line:
            # Draw horizontal lines for each qubit
            for pos, data_register in self.data.items():
                ax.hlines(y=2*pos, xmin=0, xmax=max_depth+1, color='black', linewidth=0.5)
                name = data_register.type
                cur_count = name_count[name]
                name_count[name] += 1
                
                ax.text(-0.5, 2*pos, name+f'{cur_count}', fontsize=12, ha='right', va='center')
            
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
                    self.drawCCGate(reg, gate, x, ax, if_text = if_text)
                elif isinstance(gate, LogicalGate):
                    self.drawLogicalGate(reg, gate, x, ax, if_text = if_text)
                elif isinstance(gate, GHZprep):
                    self.drawGHZprep(reg, gate, x, ax, if_text = if_text)
                else:
                    self.drawSingleGate(reg, gate, x, ax, if_text = if_text)
                    
        ax.set_ylim(-1, num_qubits)
        ax.set_xlim(0, max_depth + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout()
        plt.show()
# Drawing ends here

AbstractCircuit.teleported_Toffoli = teleported_Toffoli
AbstractCircuit.AND = AND
AbstractCircuit.unAND = unAND
AbstractCircuit.multiAnd = multiAND
AbstractCircuit.lookup = lookup
AbstractCircuit.add = add