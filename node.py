from dataclasses import dataclass
from typing import List, Optional

from bril_type import *


@dataclass(frozen=True)
class Node:
    id: int
    predecessors: List["Node"]
    successors: List["Node"]
    instr: Instruction
    label: Optional[str]

    def __str__(self):
        return f"{self.instr}"
