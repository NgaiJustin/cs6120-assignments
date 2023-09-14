from collections import deque
from typing import Dict, List, Set

import graphviz  # type: ignore

from bril_type import *
from node import Node


def to_cfg_fine_grain(bril: Program) -> List[Node]:
    """Convert a Bril program to a control flow graph (one graph for each function).)"""
    cfg_nodes = []
    for fi, func in enumerate(bril["functions"]):
        nodes: List[Node] = []
        labels: Dict[str, Node] = {}

        # Split each instruction into its own basic block
        for ii, instr in enumerate(func.get("instrs", [])):
            node = Node(
                id=f"f{fi}-{ii}",
                predecessors=set(),
                successors=set(),
                instr=instr,
                label=instr.get("label"),
            )
            nodes.append(node)

            if node.label is not None:
                labels[node.label] = node

        # Add edges between nodes
        for i in range(len(nodes) - 1):
            if nodes[i].instr.get("op") in {"jmp", "br"}:
                continue
            nodes[i].successors.add(nodes[i + 1])
            nodes[i + 1].predecessors.add(nodes[i])

        # Add edges for jmp, br
        for node in nodes:
            # jmp and br instructions have a "labels" field
            # mostly to make type-checker happy
            if "labels" not in node.instr:
                continue

            if node.instr.get("op") == "jmp":
                dest = node.instr["labels"][0]
                node.successors.add(labels[dest])
                labels[dest].predecessors.add(node)

            elif node.instr.get("op") == "br":
                dest_a, dest_b = node.instr["labels"]

                node.successors.add(labels[dest_a])
                labels[dest_a].predecessors.add(node)

                node.successors.add(labels[dest_b])
                labels[dest_b].predecessors.add(node)

        cfg_nodes.extend(nodes)

    return cfg_nodes


def cfg_visualize(cfg_nodes: List[Node]):
    """Visualize a control flow graph using graphviz.

    Paste output in https://edotor.net/ for a pretty diagram"""
    import briltxt  # type: ignore

    print("Visualizing CFG")
    g = graphviz.Digraph()

    # Initialize nodes
    for node in cfg_nodes:
        g.node(
            node.id,
            briltxt.instr_to_string(node.instr)
            if "op" in node.instr
            else f"LABEL <{node.instr.get('label')}>",  # must be label
        )

    # key: node id
    # value: 0 = unvisited, -1 = visiting, 1 = visited
    visit_state: Dict[str, int] = {node.id: 0 for node in cfg_nodes}

    q: deque[Node] = deque(cfg_nodes)

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
