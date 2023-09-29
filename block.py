from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from node import PhiNode

import graphviz  # type: ignore

from bril_type import *


@dataclass
class Block:
    id: str  # f0-0, f0-1, etc.
    label: str  # label name, if any
    predecessors: Set["Block"]
    successors: Set["Block"]
    instrs: List[Instruction]

    # key: var_name_before_rename, value: PhiNode
    phi_nodes: Optional[Dict[str, PhiNode]] = None

    def __str__(self):
        return f"{self.instrs}"

    def __repr__(self):
        return f"{self.instrs}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Block) and self.id == other.id

    def __lt__(self, other):
        self_fi, self_ii = self.id.split("-")
        self_fi, self_ii = int(self_fi[1:]), int(self_ii)

        other_fi, other_ii = other.id.split("-")
        other_fi, other_ii = int(other_fi[1:]), int(other_ii)

        return (self_fi, self_ii) < (other_fi, other_ii)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "predecessors": [block.id for block in self.predecessors],
            "successors": [block.id for block in self.successors],
            "instrs": self.instrs,
            "phi_node": self.phi_nodes,
        }


def to_bril(blocks: List[Block]) -> List[Instruction]:
    """
    Convert a RootNode back to a Bril Function
    """
    instrs = []
    for block in blocks:
        instrs.extend(block.instrs)
    return instrs


def visualize(blocks: List[Block]) -> str:
    """
    Visualize a block based graph (CFG, Dominator Tree, etc.) using graphviz from a list of blocks.

    Paste output in https://edotor.net/ for a pretty diagram
    """
    import briltxt  # type: ignore

    g = graphviz.Digraph()

    # Initialize blocks
    for block in sorted(blocks):
        block_desc = ""
        if block.phi_nodes is not None:
            block_desc += "PHI:\\n"
            for _, phi in block.phi_nodes.items():
                block_desc += f"{phi.dest}: "
                for block_id, renamed_var in phi.args.items():
                    block_desc += f"{block_id} -> {renamed_var}, "
                block_desc += "\\n"

            block_desc += "\\n"

        for instr in block.instrs:
            block_desc += (
                briltxt.instr_to_string(instr)
                if "op" in instr
                else f"LABEL <{instr.get('label')}>"  # must be label
            )
            block_desc += "\\n"

        g.node(block.id, block_desc, shape="Msquare" if block.phi_nodes else "rect")

    # key: block id
    # value: 0 = unvisited, -1 = visiting, 1 = visited
    visit_state: Dict[str, int] = {block.id: 0 for block in blocks}

    q: deque[Block] = deque(blocks)

    while len(q) > 0:
        block = q.pop()

        if visit_state[block.id] == 1:  # Already visited
            continue
        elif visit_state[block.id] == -1:  # Loop
            visit_state[block.id] = 1
        else:
            for next_block in block.successors:
                a = block.id
                b = next_block.id
                g.edge(a, b)

                if visit_state[next_block.id] == 1:
                    q.append(next_block)
                    visit_state[next_block.id] = -1

    # print(g.source)
    return g.source
