from dataclasses import dataclass
from typing import List, Optional

from bril_type import *


@dataclass(frozen=True)
class Node:
    predecessors: List["Node"]
    successors: List["Node"]
    instr: Instruction
    label: Optional[str]
