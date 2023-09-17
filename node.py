from dataclasses import dataclass
from typing import Optional, Set

from bril_type import *


@dataclass(frozen=True)
class Node:
    id: str
    predecessors: Set["Node"]
    successors: Set["Node"]
    instr: Instruction
    label: Optional[str]

    def __str__(self):
        return f"{self.instr}"

    def __repr__(self):
        return f"{self.instr}"

    def __hash__(self):
        return hash(self.id)
