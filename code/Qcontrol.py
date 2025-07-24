import numpy as np
from Bint import *
from typing import List, Union, Callable, Tuple
from Qint import Qint
from random import randint, random

class Cvalue():
    def __init__(self,
                 value: int,
                 length: int):
        self.length = length
        bin_str = bin(value)[2:].zfill(length)
        self.binary = bin_str
        self.value = value
    
    def __getitem__(self, pos):
        if isinstance(pos, int):
            new_binary = self.binary[(-1-pos)]
            new_value  = int(new_binary, 2)
            return Cvalue(new_value, 1)
        elif isinstance(pos, slice):
            start = pos.start or 0
            stop = pos.stop
            step = pos.step or 1
            new_binary = ''.join(self.binary[-1 - i] for i in range(stop - 1, start - 1, -step))
            new_value  = int(new_binary, 2)
            return Cvalue(new_value, stop - start)
        elif isinstance(pos, List) or isinstance(pos, Tuple):
            new_binary = ''.join(self.binary[-1-i] for i in reversed(pos))
            new_value  = int(new_binary, 2)
            return Cvalue(new_value, len(pos))
        else:
            raise ValueError("Invalide index")
    
    def __len__(self):
        return self.length
    
    def __setitem__(self, 
                    key: int, 
                    value: Union[int, str]):
        old_binary = self.binary
        i = len(old_binary) - 1 - key
        new_binary = old_binary[:i] + str(value) + old_binary[i+1:]
        new_value = int(new_binary, 2)
        self.binary = new_binary
        self.value = new_value
        return None
    
    def __str__(self):
        return (self.binary)
    
    def __eq__(self, other):

        if not isinstance(other, Cvalue):
            raise ValueError("Cannot compare a Cvalue with a non Cvalue")
        if len(self) != len(other):
            return False
        elif self.binary == other.binary:
            return True
        return False

    def pop(self, pos: Union[int, List[int]]):
        if isinstance(pos, int):
            cut_pos = self.length-pos-1
            new_binary = self.binary[:cut_pos] + self.binary[cut_pos+1:]
            new_length = self.length - 1
        elif isinstance(pos, List):
            new_binary = ''.join(bit for i, bit in enumerate(self.binary) if (self.length - i - 1) not in pos)
            new_length = self.length - len(pos)
        new_value = int(new_binary, 2)
        return Cvalue(new_value, new_length)

class Qcontrol():
    def __init__(self, 
                 values: List[Cvalue], 
                 amps: List[np.complexfloating], 
                 length: int):
        if len(amps) != 2**length:
            raise ValueError("Didn't specify all amps for controlled qubits")
        self.values = values
        self.amps = amps
        self.length = length

    def __len__(self):
        return self.length
    
    def qalloc(num, basis):
        if basis == "X":
            values = list(range(0,2**num))
            values = [Cvalue(value, num) for value in values]
            amps = np.repeat(1/2**(num/2), 2**num)
            module = 2**num
            length = num
        if basis == "Z":
            values = [Cvalue(0, num)]
            amps = [1]
            module = 2**num
            length = num
        return Qcontrol(values, amps, length)
    
    
class Qregister():
    def __init__(self, 
                 values: List[Union[Cvalue, BinaryInt]],
                 amps: List[np.complex128],
                 module: int,
                 length: int):
        if len(amps) != 2**length:
            raise ValueError("Didn't specify all amps for Qregister")
        if abs(np.linalg.norm(amps) - 1) > 1e-7:
            raise ValueError("Unnormalized Qregister")
        else:
            amps = amps / np.linalg.norm(amps)
        

        self.values = values
        self.amps = amps
        self.module = module
        self.length = length
        

    def __str__(self):
        output = ""
        for value in self.values:
            qc_value = value[0]
            qt_value = value[1]
            cur_amp = self.amps[qc_value.value * 2**(len(qt_value)) + qt_value.value]
            output += f"{cur_amp} → {qc_value.binary}|{qt_value.binary}\n"
        return output
    
    def __len__(self):
        return self.length
    
    def __matmul__(self,
                   other):
        if len(self) != len(other):
            raise ValueError("Cannot multiply two qubits with different length")
        amp1 = self.amps
        amp2 = other.amps
        return np.vdot(amp1, amp2)

    def find_measurement_outcome(self, 
                                 pos_lst: List[int], 
                                 basis: str) -> Cvalue:
        data_qubit = self.values[0][1]
        control_qubit = self.values[0][0]
        prob_lst = np.zeros([2**len(pos_lst), 2**(data_qubit.length + control_qubit.length - len(pos_lst))], dtype=np.complex128)
        qc_length = len(self.values[0][0])
        qt_length = len(self.values[0][1])
        if basis == "X":
            for k in range(2**len(pos_lst)):
                cur_observables = Cvalue(k, len(pos_lst))
                for j in range(len(self.values)):
                    value = self.values[j]
                    cvalue = value[0]
                    cur_data = value[1]
                    cur_cvalue = cvalue[pos_lst]
                    neg = if_neg(cur_cvalue, cur_observables)
                    if len(cvalue) > len(pos_lst):
                        left_cvalue = cvalue.pop(pos_lst)
                        column_index = cur_data.value + left_cvalue.value*2**cur_data.length
                    elif len(cvalue) == len(pos_lst):
                        column_index = cur_data.value
                    else:
                        raise ValueError("Measure more controls than expected")
                    amp_index = cvalue.value*2**qt_length + cur_data.value
                    # print("====")
                    # print(cvalue.value, cur_data.value)
                    # print(self.amps[amp_index], amp_index)
                    prob_lst[k][column_index] += neg * self.amps[amp_index] / np.sqrt(2**len(pos_lst))
                    # print(prob_lst)
        elif basis == "Z":
            for k in range(2**len(pos_lst)):
                cur_observables = Cvalue(k, len(pos_lst))
                for j in range(len(self.values)):
                    value = self.values[j]
                    cvalue = value[0]
                    cur_data = value[1]
                    cur_cvalue = cvalue[pos_lst]
                    if len(cvalue) > len(pos_lst):
                        left_cvalue = cvalue.pop(pos_lst)
                        column_index = cur_data.value + left_cvalue.value*2**cur_data.length
                    elif len(cvalue) == len(pos_lst):
                        column_index = cur_data.value
                    if cur_cvalue == cur_observables:
                        # print(left_cvalue.value, k, column_index)
                        amp_index = cvalue.value*2**qt_length + cur_data.value
                        prob_lst[k][column_index] += self.amps[amp_index]
        else:
            raise ValueError("invalid measurement basis")
        prob_lst = np.abs(prob_lst)**2
        prob_lst = np.sum(prob_lst, axis=1)
        # print(prob_lst)
        if abs(sum(prob_lst) - 1) > 1e-7:
            raise ValueError("Unnormalized probability vector")
        p = np.random.rand()
        p_accum = 0
        measurement_outcom = []
        for k in range(len(prob_lst)):
            p_accum += prob_lst[k]
            if p < p_accum:
                measurement_outcom = Cvalue(k, len(pos_lst))
                break
        if isinstance(measurement_outcom, List):
            raise ValueError("No outcome found")
        return measurement_outcom

    def measure_controls(self, 
                         pos_lst: List[int], 
                         basis: str) -> Tuple[Qint, List[int]]:
        observables = self.find_measurement_outcome(pos_lst, basis)
        result_values = []
        result_amps = np.zeros(2**(len(self) - len(pos_lst)), dtype=np.complex128)
        if_all_measured = (len(pos_lst) == len(self.values[0][0]))
        if len(pos_lst) > len(set(pos_lst)):
            raise ValueError("Meaningless to measure a qubit for twice")
        if basis == "X":
            for i in range(len(self.values)):
                value = self.values[i]
                cvalue = value[0]
                data = value[1]
                measured_cvalue = cvalue[pos_lst]
                amp_index = cvalue.value * 2**len(data) + data.value
                new_amp = self.amps[amp_index] * if_neg(measured_cvalue, observables)
                if not if_all_measured:
                    new_cvalue = cvalue.pop(pos_lst)
                    result_values.append([new_cvalue, data])
                    result_amps[new_cvalue.value * 2**len(data) + data.value] += new_amp
                else:
                    result_values.append(data)
                    result_amps[data.value] += new_amp
                
        elif basis == "Z":
            for i in range(len(self.values)):
                value = self.values[i]
                cvalue = value[0]
                data = value[1]
                measured_cvalue = cvalue[pos_lst]
                amp_index = cvalue.value * 2**len(data) + data.value
                if measured_cvalue == observables:
                    if not if_all_measured:
                        # print(measured_cvalue, "m")
                        # print(observables, "obs")
                        # print(cvalue, "control")
                        # print(data, "data")
                        new_cvalue = cvalue.pop(pos_lst)
                        result_values.append([new_cvalue, data])
                        result_amps[new_cvalue.value * 2**len(data) + data.value] += self.amps[amp_index]
                    else:
                        result_values.append(data)
                        result_amps[data.value] += self.amps[amp_index]
        else:
            raise ValueError("Invalid measurement basis")
        
        result_amps = result_amps/(np.linalg.norm(result_amps))
        if if_all_measured:
            result_qubit = Qint(result_values, result_amps, self.module, self.length-len(pos_lst)) 
        else:
            result_qubit = Qregister(result_values, result_amps, self.module, self.length-len(pos_lst))
        return [result_qubit, observables]

def if_neg(outbits: Cvalue, observables: Union[List[int], Cvalue])->int:
    if len(outbits) != len(observables):
        raise ValueError("Cannot compare two bits with different length")
    if isinstance(observables, Cvalue):
        observables = [int(bit) for bit in observables.binary]
    bits = str(outbits)
    result = 1
    for i in range(len(outbits)):
        cur_bit = int(bits[i], 2)
        result *= (-1)**(cur_bit * observables[i])
    return result

def controlled_by(qc: Union[int, Qcontrol],
                qt:Qint,
                offset:Union[int, List[int]],
                f: Callable[[BinaryInt, int], BinaryInt]):
    if qc == 0:
            pass
    elif qc == 1:
        if isinstance(offset, int):
            result_values = [f(xi, offset).value for xi in qt.values]
            result_amps = qt.amps
            result_length = qt.length
            result_module = qt.module
            return Qint(result_values, result_amps, result_module, result_length)
        else:
            raise ValueError("Cannot load more than 1 integer with classical control")

    elif isinstance(qc, Qcontrol):
        if len(offset) > 1:
            # result_values = [[c, (f(t, offset[c.value]))] 
            #         for c in qc.values for t in qt.values]
            result_values = []
            result_amps = np.zeros(2**(len(qt)+len(qc)), dtype=np.complex128)
            for c in qc.values:
                for t in qt.values:
                    result_t_value = f(t, offset[c.value])
                    result_values.append([c, result_t_value])
                    result_amps[2**len(qt)*c.value + result_t_value.value] = qc.amps[c.value] * qt.amps[t.value]
            result_length = qc.length+qt.length
            result_module = qt.module
            return Qregister(result_values, result_amps, result_module, result_length)
        else:
            raise ValueError("A single integer table can be loaded by a classical control")
    else:
        raise ValueError("Invalid Control. Controls is either classical or quantum.")
    