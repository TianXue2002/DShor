from Qcontrol import *
import numpy as np

def coset_preparation(qint:Qint, 
                      m:int)->Qcontrol:
    q_coset = qint << 2
    