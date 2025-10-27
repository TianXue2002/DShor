from Qint import *
from QPU import *
def approx_exp(Q_exp:Qint,
               config,
               qpu: QPU):
    Qd_log = qpu.allocate_qubits(config.qd_len)
    Q_result = qpu.allocate_qubits(config.result_len)
    pass

def loop1(Q_exp: Qint,
          Qd_log: Qint,
          i: int,
          config):
    for j in range(config.w1):
        Q_k = Q_exp[j * config.w1: (j+1) * config.w1]
        table = config.lookup1[i, j]
        lookup = LookupTable(Q_k, table)
        Qd_log += lookup
    return

def loop2(Q_target: Qint,
          Q_add: Qint,
          module: int,
          compressed_len :int):
    assert compressed_len >= module.bit_length() 
    n = len(Q_target)
    while n > compressed_len:
        n -= 1
        offset = module << (n - module.bit_length())
        # Q_target[:n+1] -= offset
        # if n <= len(Q_target) - 2:
        #     print((Q_target.data))
        Q_tmp = Q_target[:n+1]
        Q_tmp -= offset
        table = {0:0, 1:offset}
        # print(Q_target[n+1])
        ghz_lookup = LookupTable(Q_target[n], table)
        Q_tmp = Q_target[:n+1]
        Q_tmp += ghz_lookup
        # result = Q_tmp[n].mx_rz()
        # print(result, "result")
        # Q_tmp[n].zgeq(offset)
    Q_target.remove(range(compressed_len + 1, len(Q_target)))

def loop3(config,
          Qd_log: Qint,
          i: int,
          qpu: QPU):
    module = config.periods[i]
    Q_r = qpu.allocate_qubits(module.bit_length() + 1)
    Q_h = qpu.allocate_qubits(module.bit_length() + 1)
    table = config.initial_table3[i]
    Q_l = Qd_log[:config.window3a * 2]
    lookup = LookupTable(Q_l, table)
    Q_r ^= lookup
    for j in range(2, config.num_window3a):
        Ql_1 = Q_l[j*config.window3a: (j+1)*config.window3a]
        for k in range(2, config.num_window3b):
            Ql_0 = Q_r[k*config.window3b: (j+1)*config.window3b]
            lookup = LookupTable([Ql_1, Ql_0])