from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import graphviz  # type: ignore

from bril_type import *


@dataclass
class PhiNode:
    dest: str
    args: Dict[str, str]  # {node.id -> renamed_var_name}

    def to_dict(self):
        return {
            "dest": self.dest,
            "args": self.args,
        }


@dataclass
class Node:
    id: str
    predecessors: Set["Node"]
    successors: Set["Node"]
    instr: Instruction
    label: Optional[str]

    # key: var_name_before_rename, value: PhiNode
    phi_nodes: Optional[Dict[str, PhiNode]] = None

    def __str__(self):
        return f"{self.instr}"

    def __repr__(self):
        return f"{self.instr}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id

    def __lt__(self, other):
        self_fi, self_ii = self.id.split("-")
        self_fi, self_ii = int(self_fi[1:]), int(self_ii)

        other_fi, other_ii = other.id.split("-")
        other_fi, other_ii = int(other_fi[1:]), int(other_ii)

        return (self_fi, self_ii) < (other_fi, other_ii)

    def to_dict(self):
        return {
            "id": self.id,
            "predecessors": [node.id for node in self.predecessors],
            "successors": [node.id for node in self.successors],
            "instr": self.instr,
            "label": self.label,
            "phi_node": self.phi_nodes,
        }


@dataclass
class RootNode:
    func_name: str
    func_args: list[Argument]
    func_type: Type
    entry_node: Node

    def __str__(self):
        return f"{self.func_name}"

    def __repr__(self):
        return f"{self.func_name}"

    def __hash__(self):
        return hash(self.func_name)

    def __eq__(self, other):
        return isinstance(other, RootNode) and self.func_name == other.func_name

    def to_dict(self):
        return {
            "func_name": self.func_name,
            "func_args": self.func_args,
            "func_type": self.func_type,
            "entry_node": self.entry_node.to_dict(),
        }


def visualize(entry_node: Node):
    """
    Visualize a node based graph (CFG, Dominator Tree, etc.) using graphviz from an entry node.

    Paste output in https://edotor.net/ for a pretty diagram
    """
    if len(entry_node.predecessors) != 0:
        raise Exception("Entry node must have no predecessors")

    q = deque([entry_node])
    seen: Set[Node] = set()

    while q:
        node = q.popleft()
        seen.add(node)
        q.extend([succ for succ in node.successors if succ not in seen])

    return visualize_from_nodes(list(seen))


def visualize_from_nodes(nodes: List[Node]) -> str:
    """
    Visualize a node based graph (CFG, Dominator Tree, etc.) using graphviz.

    Paste output in https://edotor.net/ for a pretty diagram
    """
    import briltxt  # type: ignore

    g = graphviz.Digraph()

    # Initialize nodes
    for node in sorted(nodes):
        node_desc = ""
        if node.phi_nodes is not None:
            node_desc += "PHI:\\n"
            for _, phi in node.phi_nodes.items():
                node_desc += f"{phi.dest}: "
                for node_id, renamed_var in phi.args.items():
                    node_desc += f"{node_id} -> {renamed_var}, "
                node_desc += "\\n"

            node_desc += "\\n"

        node_desc += (
            briltxt.instr_to_string(node.instr)
            if "op" in node.instr
            else f"LABEL <{node.instr.get('label')}>"  # must be label
        )

        g.node(node.id, node_desc, shape="Msquare" if node.phi_nodes else None)

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
                a = node.id
                b = next_node.id
                g.edge(a, b)

                if visit_state[next_node.id] == 1:
                    q.append(next_node)
                    visit_state[next_node.id] = -1

    # print(g.source)
    return g.source
