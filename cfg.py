import json
from collections import deque
from typing import Dict, List, Set

import graphviz

from bril_type import *
from node import Node


def to_cfg_fine_grain(bril: Program) -> List[Node]:
    """Convert a Bril program to a control flow graph (one graph for each function).)"""
    cfgs = []
    for func in bril["functions"]:
        nodes: List[Node] = []
        labels: Dict[str, Node] = {}

        # Split each instruction into its own basic block
        for i, instr in enumerate(func.get("instrs", [])):
            node = Node(
                id=i,
                predecessors=[],
                successors=[],
                instr=instr,
                label=instr.get("label"),
            )
            nodes.append(node)

            if node.label is not None:
                labels[node.label] = node

        # Add edges between nodes
        for i in range(len(nodes) - 1):
            nodes[i].successors.append(nodes[i + 1])
            nodes[i + 1].predecessors.append(nodes[i])

        # Add edges for jmp, br
        for node in nodes:
            # jmp and br instructions have a "labels" field
            # mostly to make type-checker happy
            if "labels" not in node.instr:
                continue

            if node.instr.get("op") == "jmp":
                dest = node.instr["labels"][0]
                node.successors.append(labels[dest])
                labels[dest].predecessors.append(node)

            elif node.instr.get("op") == "br":
                dest_a, dest_b = node.instr["labels"]

                node.successors.append(labels[dest_a])
                labels[dest_a].predecessors.append(node)

                node.successors.append(labels[dest_b])
                labels[dest_b].predecessors.append(node)

        cfgs.append(nodes[0])

    return cfgs


def cfg_visualize(cfg_root_node: Node):
    print("Visualizing CFG")
    g = graphviz.Digraph()
    seen: Set[int] = set()
    q = deque([cfg_root_node])

    while len(q) > 0:
        node = q.popleft()

        g.node(str(node.id), str(node.instr))

        for next_node in node.successors:
            g.node(str(next_node.id), str(next_node.instr))
            g.edge(str(node.id), str(next_node.id))

            if node.id not in seen:
                q.append(next_node)
                seen.add(node.id)

    print(g.source)
    return g.source
