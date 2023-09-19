"""
A series of dominance utilities functions including
- Constructing the dominance tree [-t]
- Computing the dominance frontier [-f]
"""
import sys
from collections import deque
from typing import Dict, List, Set

from bril_type import *
from cfg import get_entry_nodes, to_cfg_fine_grain
from node import Node, visualize
from utils import load


def strictly_dominates(node_a: Node, node_b: Node, b_dominators: Set[Node]) -> bool:
    """
    Return true if node_a strictly dominates node_b.
    """
    return node_a in b_dominators and node_a != node_b


def _get_dominators(entry: Node) -> Dict[Node, Set[Node]]:
    """
    Return the set of dominators for all nodes in a CFG.
    """

    # get all nodes reachable from the entry node
    all_nodes: Set[Node] = set()
    q = deque([entry])
    while q:
        node = q.popleft()
        if node not in all_nodes:
            all_nodes.add(node)
            q.extend(node.successors)

    # initialize as complete relation
    dom = {node: all_nodes.copy() for node in all_nodes}
    dom[entry] = {entry}

    converged = False
    while not converged:
        converged = True

        for node in dom.keys():
            if node == entry:
                continue

            old_len = len(dom[node])

            for p in node.predecessors:
                dom[node] = dom[node].intersection(dom[p])
            dom[node].add(node)

            new_len = len(dom[node])

            converged = (old_len == new_len) and converged

    return dom


def dominance_tree(doms: Dict[Node, Set[Node]]) -> List[Node]:
    """
    Construct the dominance tree given a mapping of nodes to their dominators.
    """
    dom_tree_nodes: List[Node] = []

    for node_a, _ in doms.items():
        for node_b, b_dominators in doms.items():
            if node_a == node_b:
                if len(node_a.predecessors) == 0:
                    # init entry node
                    dom_tree_nodes.append(
                        Node(
                            id=node_a.id,
                            predecessors=set(),
                            successors=set(),
                            instr=node_a.instr,
                            label=node_a.label,
                        )
                    )
            else:
                # if A dominates B, and A does not strictly dominate any other node that strictly dominates B
                if node_a in b_dominators and not any(
                    strictly_dominates(node_a, node_c, doms[node_c])
                    for node_c in b_dominators
                    if node_c != node_b
                ):
                    print(f"{node_a.id} dominates {node_b.id}")
                    dom_tree_node = Node(
                        id=node_b.id,
                        predecessors=set([node_a]),  # all dominators except self
                        successors=set(),
                        instr=node_b.instr,
                        label=node_b.label,
                    )
                    dom_tree_nodes.append(dom_tree_node)

    return dom_tree_nodes


def dominance_frontier(cfg: List[Node]) -> List[Node]:
    """
    Compute the dominance frontier of a CFG.
    """
    return cfg


if __name__ == "__main__":
    program, cli_flags = load(["-t", "-f"])

    if program is None:
        sys.exit(1)

    if not cli_flags["t"] and not cli_flags["f"]:
        print("Please specify either -t or -f")
        sys.exit(1)

    cfg_nodes = to_cfg_fine_grain(program)
    entry_nodes = get_entry_nodes(cfg_nodes)
    doms = _get_dominators(entry_nodes[0])  # TODO: pick the first function (for now)

    if "t" in cli_flags:
        t = dominance_tree(doms)
        print(visualize(t, forward=False))

    elif "f" in cli_flags:
        f = dominance_frontier(cfg_nodes)
        print(visualize(f))
