from bril_type import *
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Node:
    predecessors: List["Node"]
    successors: List["Node"]
    instr: Instruction
    label: Optional[str]
