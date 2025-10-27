from QuantumGate import LogicalGate, LookupGate, GHZprep
from typing import List, Dict
from help_function import get_depth, get_gate_cost


def raw_AND(self,
        qj: "AbstractRegister",
        a: "AncillaRegister",
        truth_table: List[bool],
        gate_cost = None):
    
    tM, tT, tInter = get_gate_cost(gate_cost)

    cur_depth = max([self.depth, qj.depth, a.depth])
    g = LogicalGate(self, qj, a, truth_table, "AND")
    g.depth = cur_depth
    gate_length = 3 + 3*tT
    g.length = gate_length
    self.append(cur_depth, g, length = gate_length)
    qj.append(cur_depth, g, length = gate_length)
    a.append(cur_depth, g, length = gate_length)

def raw_UNAND(self,
        qj: "AbstractRegister",
        a: "AncillaRegister",
        truth_table: List[bool],
        gate_cost = None):
    
    tM, tT, tInter = get_gate_cost(gate_cost)
    gate_length = tM + 1
    cur_depth = max([self.depth, qj.depth, a.depth])
    g = LogicalGate(self, qj, a, truth_table, "UNAND")
    g.depth = cur_depth
    g.length = gate_length
    self.append(cur_depth, g, length = gate_length)
    qj.append(cur_depth, g, length = gate_length)
    a.append(cur_depth, g, length = gate_length)

    a.Clear()

def raw_ghz_preparation(antena_ancilla: List["AbstractRegister"],
                        antena_assignment: List["AbstractRegister"],
                        gate_cost = None,
                        shift = 0):
    
    tM, tT, tInter = get_gate_cost(gate_cost)
    gate_length = 2*tInter+tM
    g = GHZprep(antena_ancilla, antena_assignment)
    g.length = gate_length
    antena_depth = 0

    for i in range(len(antena_assignment)):
        cur_qubit = antena_assignment[i][shift]
        if cur_qubit.depth > antena_depth:
            antena_depth = cur_qubit.depth
    antena_depth = [antena_depth]
    aa_depth = 0
    for i in range(len(antena_ancilla)):
        cur_aa =antena_ancilla[i][shift]
        if cur_aa.depth > aa_depth:
            aa_depth = cur_aa.depth
    aa_depth = [aa_depth]
    max_depth = max(antena_depth + aa_depth) + 1
    g.depth = max_depth
    g.shift = shift
    antena_00 = antena_assignment[0][-1]
    antena_00.append(max_depth, g, length = gate_length)
    for i in range(len(antena_assignment)):
        qubit = antena_assignment[i][shift]
        qubit.append(max_depth, g, length=gate_length)

    for i in range(len(antena_ancilla)):
        qubit = antena_ancilla[i][shift]
        qubit.append(max_depth, g, length=gate_length)
    

def raw_lookup(control_qubit:"AbstractRegister",
                target_qubits: List["AbstractRegister"],
                targets: List[bool],
                QPU_assignment: Dict[int, List["AbstractRegister"]],
                antena_assignment: List["AbstractRegister"],
                antena_ancilla: List["AbstractRegister"],
                gate_cost = None,
                shift = 0):
    
    tM, tT, tInter = get_gate_cost(gate_cost)

    max_len = 0
    pre_depth = 0
    for i in range(len(antena_assignment.values())):
        if i == 0:
            cur_depth = max(get_depth([antena_assignment[0][-1], antena_assignment[0][shift]]))
        else:
            cur_depth = antena_assignment[i][shift].depth
        if cur_depth > pre_depth:
            pre_depth = cur_depth

    for qubit_lst in antena_ancilla.values():
        cur_depth = max(get_depth(qubit_lst))
        if cur_depth > pre_depth:
            pre_depth = cur_depth

    raw_ghz_preparation(antena_ancilla, antena_assignment, gate_cost=gate_cost, shift = shift)

    for i in range(1, len(QPU_assignment)):
        cur_qubits = QPU_assignment[i]
        if antena_assignment[i-1] != []:
            cur_antena = antena_assignment[i-1][shift]
        else:
            cur_antena = []
        cur_aa = None
        if i < len(QPU_assignment) - 1:
            cur_aa = antena_ancilla[i-1][shift]

        cur_length = 0
        max_depth = 0

        control_depth = control_qubit.depth
        target_depth = max(get_depth(cur_qubits))
        if not isinstance(cur_antena, List):
            antena_depth = cur_antena.depth
        else:
            antena_depth = 0
        aa_depth = 0 if i >= len(QPU_assignment) - 2 else cur_aa.depth
        cur_depth = max([pre_depth, target_depth, antena_depth, aa_depth]) + 1
        for k in range(len(targets)):
            target = targets[k]
            if target == False and target_qubits[k] in cur_qubits:
                cur_length += 1
        g = LookupGate(targets, control_qubit, target_qubits, QPU_assignment,
                   antena_assignment, antena_ancilla)
        g.length = cur_length
        g.depth = cur_depth
        g.shift = shift

        if cur_depth + cur_length > max_depth:
            max_depth = cur_depth + cur_length

        if cur_length > max_len:
            max_len = cur_length
        if cur_length != 0:
            cur_antena.append(cur_depth, g, length=cur_length)
            # if i < len(QPU_assignment) - 1:
            #     cur_aa.append(cur_depth, g, length = cur_length)
            for qubit in cur_qubits:
                qubit.append(cur_depth, g, length = cur_length)
    
    g = LookupGate(targets, control_qubit, target_qubits, QPU_assignment,
                   antena_assignment, antena_ancilla)
    control_depth = max([control_depth, antena_assignment[0][-1].depth, max_depth])
    g.depth = control_depth + 1
    g.length = 1 + tM
    control_qubit.append(control_depth + 1, g, length = 1)
    antena_assignment[0][-1].append(control_depth + 1, g, length = 1)
    return