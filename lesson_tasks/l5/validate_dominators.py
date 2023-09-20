"""
This module contains functions that validate the dominator relationships between blocks in a CFG.
"""
from typing import List, Set
from collections import deque

from bril_type import *
from node import Node


def validate_dominators(
    cfg_nodes: List[Node],
    entry_node: Node,
    node_a: Node,
    node_b: Node,
) -> bool:
    """
    Return true if node_a dominates node_b.

    A dominator is a node that is on every path from the entry node to a given node.
    """
    # validate entry node
    if entry_node not in cfg_nodes or len(entry_node.predecessors) != 0:
        raise Exception("Invalid entry node")

    # validate node_a and node_b
    if node_a not in cfg_nodes:
        raise Exception("Invalid node_a")
    if node_b not in cfg_nodes:
        raise Exception("Invalid node_b")

    paths: Set[List[Node]] = set()
    q: deque[List[Node]] = deque([[entry_node]])

    while q:
        path = q.popleft()
        last_node = path[-1]
        if last_node == node_b:
            paths.add(path)
        elif len(last_node.successors) != 0:
            for next_node in last_node.successors:
                q.append(path + [next_node])

    return all(node_a in path for path in paths)


def validate_strictly_dominates(
    cfg_nodes: List[Node],
    entry_node: Node,
    node_a: Node,
    node_b: Node,
) -> bool:
    """
    Return true if node_a strictly dominates node_b.

    A strictly dominates B iff A dominates B and A ≠ B.
    """
    return (
        validate_dominators(cfg_nodes, entry_node, node_a, node_b) and node_a != node_b
    )
