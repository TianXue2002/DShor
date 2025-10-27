from collections import defaultdict
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from QuantumGate import *

# === Fast drawer for batch rendering ===
class FastDrawer:
    def __init__(self):
        self.rectangles = []
        self.texts = []
        self.circles = []

    def add_rect(self, x, y, w, h, facecolor='red', edgecolor='black', alpha = 1):
        self.rectangles.append((Rectangle((x, y), w, h), facecolor, edgecolor, alpha))

    def add_text(self, x, y, text, **kwargs):
        self.texts.append((x, y, text, kwargs))

    def add_circle(self, x, y, radius=0.2, fill=False, edgecolor='black', linewidth=1.5):
        self.circles.append(Circle((x, y), radius, fill=fill, edgecolor=edgecolor, linewidth=linewidth))

    def draw_all(self, ax):
        if self.rectangles:
            rects, fcs, ecs, alpha = zip(*self.rectangles)
            pc = PatchCollection(rects)
            pc.set_facecolor(fcs)   # use individual face colors
            pc.set_edgecolor(ecs)   # use individual edge colors
            pc.set_alpha(alpha)
            ax.add_collection(pc)
        for circle in self.circles:
            ax.add_patch(circle)
        for x, y, s, kwargs in self.texts:
            ax.text(x, y, s, **kwargs)

# === Circuit drawer using FastDrawer ===
class CircuitDrawer:

    def drawGHZprep(self, reg, gate, x, drawer, if_text=False):
        shift = gate.shift
        if reg == gate.antena_assignment[0][shift]:
            pos_lst = []
            for i in range(len(gate.antena_ancilla)):
                q = gate.antena_ancilla[i][shift]
                pos_lst.append(2*q.pos + (q.get_type() == "ancilla"))
            for i in range(len(gate.antena_assignment)):
                q = gate.antena_assignment[i][shift]
                pos_lst.append(2*q.pos + (q.get_type() == "ancilla"))
            y0, y1 = min(pos_lst), max(pos_lst)
            if shift == 0:
                color = "red"
            else:
                color = "yellow"
            drawer.add_rect(gate.depth - 0.2, y0 - 0.2, gate.length, 0.4 + y1 - y0, facecolor=color, 
                            edgecolor='black', alpha=0.5)
            if if_text:
                drawer.add_text(gate.depth + gate.length/2 - 0.2, (y0 + y1)/2, "GHZ Prep",
                                ha='center', va='center', fontsize=15)
        return 
    
    def drawSingleGate(self, reg, gate, x, drawer, cc=False, if_text=False):
        patch_color = "blue" if cc else "lightblue"
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        drawer.add_rect(x - 0.2, y - 0.2, 0.4, 0.4, facecolor=patch_color, edgecolor='black')
        if if_text:
            drawer.add_text(x, y, gate.type, ha='center', va='center', fontsize=8)

    def drawTwoQubitGate(self, reg, gate, x, drawer, cc=False):
        gate_color = "blue" if cc else "black"
        control, target = gate.control, gate.target
        y = 2*reg.pos + (reg.get_type()=="ancilla")
        y_ref = 2*control.pos + (control.get_type()=="ancilla")
        if y != y_ref:
            return
        y_control = y_ref
        y_target = 2*target.pos + (target.get_type()=="ancilla")
        plt.plot([x, x], [y_control, y_target], color=gate_color, linewidth=1)
        drawer.add_text(x, y_control, "•", color=gate_color)
        if gate.type == "CNOT":
            drawer.add_circle(x, y_target, fill=False, edgecolor=gate_color)
            plt.plot([x, x], [y_target-0.2, y_target+0.2], color=gate_color, linewidth=1)
            plt.plot([x-0.2, x+0.2], [y_target, y_target], color=gate_color, linewidth=1)
        elif gate.type == "CZ":
            drawer.add_text(x, y_target, "•", color=gate_color)

    def drawToffoli(self, reg, gate, x, drawer):
        c1 = 2*gate.c1.pos + (gate.c1.get_type() == "ancilla")
        c2 = 2*gate.c2.pos + (gate.c2.get_type() == "ancilla")
        target = 2*gate.target.pos + (gate.target.get_type() == "ancilla")
        y = 2*reg.pos + (reg.get_type()=="ancilla")
        if y != c1:
            return
        plt.plot([x, x], [max(c1,c2), target], color='black', linewidth=1)
        drawer.add_text(x, c1, "•")
        drawer.add_text(x, c2, "•")
        drawer.add_circle(x, target)

    def drawLogicalGate(self, reg, gate, x, drawer, if_text=False):
        if reg != gate.qi:
            return
        yi = 2*gate.qi.pos + (gate.qi.get_type()=="ancilla")
        yj = 2*gate.qj.pos + (gate.qj.get_type()=="ancilla")
        ya = 2*gate.a.pos + (gate.a.get_type()=="ancilla")
        y0, y1 = min(yi,yj,ya), max(yi,yj,ya)
        width = gate.length
        drawer.add_rect(x - 0.2, y0 - 0.2, width, 0.4 + y1 - y0, facecolor='lightblue', edgecolor='black')
        if if_text:
            drawer.add_text(x+0.8, (y0 + y1)/2, gate.type, ha='center', va='center', fontsize=15)

    def drawCCGate(self, reg, gate, x, drawer, if_text=False):
        y = 2*reg.pos + (reg.get_type() == "ancilla")
        cc = gate.cc
        cur_gate = gate.gate
        targets = gate.targets
        y_ref = 2*cc.pos + (cc.get_type() == "ancilla")
        if y != y_ref and not gate.repeat:
            return
        if gate.repeat:
            y_ref = 2*targets[0].pos + (targets[0].get_type() == "ancilla")
            if y != y_ref:
                return
        if not gate.repeat:
            Mgate = QuantumGate("MX" if gate.basis=="X" else "MZ", cc.pos)
            self.drawSingleGate(reg, Mgate, x, drawer, cc=True, if_text=if_text)
        offset = 0.03
        if isinstance(cur_gate, TwoQubitGate):
            self.drawTwoQubitGate(targets[0], cur_gate, x, drawer, cc=True)
        else:
            self.drawSingleGate(targets[0], cur_gate, x, drawer, cc=True)

    def drawLookUp(self, reg, gate, x, drawer, if_text=False):
        plot = False
        if reg == gate.control:
            plot = True
            index = 0
            targets = [gate.control]
            antena_qubits = [gate.antena_assignment[0][0]]
            aa = []
        else:
            for k in range(len(gate.QPU_assignment)):
                if reg in gate.QPU_assignment[k]:
                    plot = True
                    index = k
                    shift = gate.shift
                    targets = gate.QPU_assignment[index]
                    antena_qubits = gate.antena_assignment[index - 1][shift]
                    antena_qubits = [antena_qubits]
                    if k != len(gate.QPU_assignment) - 1:
                        aa = gate.antena_ancilla[index - 1]
                    else:
                        aa = []
                    break
        if plot:
            QPU_assigment = gate.QPU_assignment
            # antena_assignment = gate.antena_assignment
            # antena_ancilla = gate.antena_ancilla
            # targets = QPU_assigment[index]
            # antena_qubits = antena_assignment[index]
            # aa = antena_ancilla[index]
            pos_lst = [2*q.pos + (q.get_type() == "ancilla") 
                    for q in targets + antena_qubits + aa]
            y0, y1 = min(pos_lst), max(pos_lst)
            drawer.add_rect(gate.depth + 0.2, y0 - 0.4, gate.length, 0.4 + y1 - y0, facecolor='blue', 
                            edgecolor='black', alpha=0.1)
            if if_text:
                drawer.add_text(gate.depth + gate.length/2 - 0.2, (y0 + y1)/2, "Lookup",
                                ha='center', va='center', fontsize=15)
        return

    def draw_circuit(self, if_text=False, if_line=False):
        all_registers = list(self.data.values()) + list(self.ancilla.values())
        num_qubits = 2*len(self.data) + 1
        max_depth = max([reg.depth for reg in all_registers], default=0)
        fig, ax = plt.subplots(figsize=(40, 30))
        plt.rcParams["figure.dpi"] = 80
        drawer = FastDrawer()

        # Horizontal lines and labels
        if if_line:
            name_count = defaultdict(int)
            for pos, reg in self.data.items():
                ax.hlines(2*pos, 0, max_depth+1, color='black', linewidth=0.5)
                name = reg.type
                drawer.add_text(-0.5, 2*pos, name + str(name_count[name]), fontsize=12, ha='right', va='center')
                name_count[name] += 1
            for pos, reg in self.ancilla.items():
                ax.hlines(2*pos+1, 0, max_depth+1, color='red', linewidth=0.5)
                drawer.add_text(-0.5, 2*pos+1, f'a{pos}', fontsize=12, ha='right', va='center')

        # Draw gates
        for reg in all_registers:
            for depth, gate in reg.gates.items():
                x = depth + 0.5
                if isinstance(gate, TwoQubitGate):
                    self.drawTwoQubitGate(reg, gate, x, drawer)
                elif isinstance(gate, ToffoliGate):
                    self.drawToffoli(reg, gate, x, drawer)
                elif isinstance(gate, CCGate):
                    self.drawCCGate(reg, gate, x, drawer, if_text=if_text)
                elif isinstance(gate, LogicalGate):
                    self.drawLogicalGate(reg, gate, x, drawer, if_text=if_text)
                elif isinstance(gate, GHZprep):
                    self.drawGHZprep(reg, gate, x, drawer, if_text=if_text)
                elif isinstance(gate, LookupGate):
                    self.drawLookUp(reg, gate, x, drawer, if_text=if_text)
                else:
                    self.drawSingleGate(reg, gate, x, drawer, if_text=if_text)

        drawer.draw_all(ax)
        ax.set_ylim(-1, num_qubits)
        ax.set_xlim(0, max_depth+1)
        # ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout()
        plt.show()

