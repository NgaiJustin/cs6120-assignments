from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import graphviz  # type: ignore

from bril_type import *


@dataclass(frozen=True)
class PhiNode:
    # new_var_name -> {node.id -> old_var_name}
    phi_dict: Dict[str, Dict[str, str]] = {}

    def add_var(self, new_var_name: str, node_id: str, old_var_name: str):
        """
        Add a new variable to the phi node. If the variable already exists, do nothing.
        """
        if new_var_name not in self.phi_dict:
            self.phi_dict[new_var_name] = {}
        if node_id not in self.phi_dict[new_var_name]:
            self.phi_dict[new_var_name][node_id] = old_var_name

    def update_var(self, new_var_name: str, old_var_name: str, node_id: str):
        """
        TODO: May have to update key logic
        """
        if new_var_name not in self.phi_dict:
            raise Exception(f"Variable {new_var_name} not in phi node")
        if old_var_name not in self.phi_dict[new_var_name]:
            raise Exception(f"Variable {old_var_name} not in phi node")

        self.phi_dict[new_var_name][old_var_name] = node_id

    def to_dict(self):
        return self.phi_dict


@dataclass
class Node:
    id: str
    predecessors: Set["Node"]
    successors: Set["Node"]
    instr: Instruction
    label: Optional[str]
    phi_node: Optional[PhiNode] = None

    def __str__(self):
        return f"{self.instr}"

    def __repr__(self):
        return f"{self.instr}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def to_dict(self):
        return {
            "id": self.id,
            "predecessors": [node.id for node in self.predecessors],
            "successors": [node.id for node in self.successors],
            "instr": self.instr,
            "label": self.label,
            "phi_node": self.phi_node
            if self.phi_node is None
            else self.phi_node.to_dict(),
        }


def visualize(nodes: List[Node], forward: bool = True):
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
            for next_node in node.successors if forward else node.predecessors:
                a = node.id if forward else next_node.id
                b = next_node.id if forward else node.id
                g.edge(a, b)

                if visit_state[next_node.id] == 1:
                    q.append(next_node)
                    visit_state[next_node.id] = -1

    # print(g.source)
    return g.source
