from AbstractRegister import *
import numpy as np
from typing import List

class QPU():

    def __init__(self,
             registers = List[AbstractRegister]):
        self.registers = registers
    
    