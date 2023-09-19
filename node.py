from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import graphviz  # type: ignore

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


def visualize(nodes: List[Node]):
    """Visualize a graph (CFG, Dominator Tree, etc.) using graphviz.

    Paste output in https://edotor.net/ for a pretty diagram"""
    import briltxt  # type: ignore

    g = graphviz.Digraph()

    # Initialize nodes
    for node in nodes:
        g.node(
            node.id,
            briltxt.instr_to_string(node.instr)
            if "op" in node.instr
            else f"LABEL <{node.instr.get('label')}>",  # must be label
        )

    # key: node id
    # value: 0 = unvisited, -1 = visiting, 1 = visited
    visit_state: Dict[str, int] = {node.id: 0 for node in nodes}

    q: deque[Node] = deque(nodes)

    while len(q) > 0:
        node = q.pop()

        if visit_state[node.id] == 1:  # Already visited
            continue
        elif visit_state[node.id] == -1:  # Loop
            visit_state[node.id] = 1
        else:
            for next_node in node.successors:
                g.edge(node.id, next_node.id)

                if visit_state[next_node.id] == 1:
                    q.append(next_node)
                    visit_state[next_node.id] = -1

    # print(g.source)
    return g.source
