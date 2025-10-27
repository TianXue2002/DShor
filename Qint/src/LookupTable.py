import numpy as np
from typing import Iterator, Sequence, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from Qint import *
class LookupTable():
    def __init__(self, 
                 address:"Qint",
                 table: dict):
        self.address = address
        self.table = table