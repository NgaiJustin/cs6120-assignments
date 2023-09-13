import json
import sys
from collections import deque
from typing import Collection, Dict, List, Set

import graphviz

from bril_type import *
from node import Node


def to_cfg_fine_grain(bril: Program) -> List[Node]:
    """Convert a Bril program to a control flow graph (one graph for each function).)"""
    cfgs = []
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

        cfgs.append(nodes[0])

    return cfgs


def cfg_visualize(cfg_root_nodes: List[Node]):
    import briltxt

    print("Visualizing CFG")
    g = graphviz.Digraph()

    seen: Set[str] = set()
    q: deque[Node] = deque(cfg_root_nodes)

    while len(q) > 0:
        node = q.popleft()

        g.node(
            node.id,
            briltxt.instr_to_string(node.instr)
            if "op" in node.instr
            else str(node.instr),
        )

        for next_node in node.successors:
            g.node(
                next_node.id,
                briltxt.instr_to_string(next_node.instr)
                if "op" in next_node.instr
                else str(next_node.instr),
            )
            g.edge(node.id, next_node.id)

            if next_node.id not in seen:
                q.append(next_node)
                seen.add(next_node.id)

    print(g.source)
    return g.source
