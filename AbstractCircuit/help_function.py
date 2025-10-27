from typing import List

def num2controls(value:int,
                     L: int):
        """
        Count the number of 1's/controls for 1 value

        Inputs:
            value:      the input value
            L:          length of the value
        """
        controls = []
        bitstring = format(value, f'0{L}b')
        bitstring = list(bitstring)
        for bit in bitstring:
            controls.insert(0, bit == "0")
        return controls

def find_greatest_diff_bit(bin1: str,
                           bin2: str):
      """
      Find the MSB of two binary string
      """
      if len(bin1) != len(bin2):
            raise ValueError("Cannot compare two bit strings with different length")
      bin1 = list(bin1)
      bin2 = list(bin2)
      for i in range(len(bin1)):
            if bin1[i] != bin2[i]:
                  return len(bin1) - i - 1
            
def get_depth(qubits):
    depth_lst = []
    if qubits == None or len(qubits) == 0:
          return []
    if isinstance(qubits, List):
        for qubit in qubits:
            depth_lst.append(qubit.depth)
    elif isinstance(qubits, dict):
         for qubit_lst in qubits.values():
              for qubit in qubit_lst:
                depth_lst.append(qubit.depth)
    return depth_lst

def get_gate_cost(cost):
    if cost == None:
        tM = 1
        tT = 1
        tInter = 1
    else:
        tM = cost.tM
        tT = cost.tT
        tInter = cost.tInter
    return tM, tT, tInter