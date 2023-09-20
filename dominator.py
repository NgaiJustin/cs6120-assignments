"""
A series of dominance utilities functions including
- Constructing the dominance tree [-t]
- Computing the dominance frontier [-f]
"""
import json
import sys
from collections import deque
from typing import Dict, List, Set

from bril_type import *
from cfg import get_entry_nodes, to_cfg_fine_grain
from node import Node, visualize
from utils import load
from dot import DotFilmStrip


def strictly_dominates(node_a: Node, node_b: Node, b_dominators: Set[Node]) -> bool:
    """
    Return true if node_a strictly dominates node_b.

    A strictly dominates B iff A dominates B and A ≠ B.
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
                    dom_tree_node = Node(
                        id=node_b.id,
                        predecessors=set([node_a]),  # all dominators except self
                        successors=set(),
                        instr=node_b.instr,
                        label=node_b.label,
                    )
                    dom_tree_nodes.append(dom_tree_node)

    return dom_tree_nodes


def dominance_frontier(a: Node) -> List[Node]:
    """
    Compute the dominance frontier for a given node.

    A dominance frontier is the set of nodes that are just “one edge away” from being dominated by a given node.
    """
    # get entry node
    entry_node = a
    q = deque([entry_node])
    while q:
        temp_node = q.popleft()
        if len(temp_node.predecessors) >= 1:
            q.extend(temp_node.predecessors)
        else:
            entry_node = temp_node
            break

    doms = _get_dominators(entry_node)
    all_nodes = set(doms.keys())

    # A’s dominance frontier contains B iff A does not strictly dominate B, but A does dominate some predecessor of B.
    frontier = [
        b
        for b in all_nodes
        if not strictly_dominates(a, b, doms[b])
        and any([a in doms[pre_node_b] for pre_node_b in b.predecessors])
    ]

    return frontier


def visualize_frontier(
    key_node: Node,
    frontier: List[Node],
    doms: Dict[Node, Set[Node]],
    tree_nodes: List[Node],
    forward: bool = True,
):
    import briltxt  # type: ignore
    import graphviz  # type: ignore

    g = graphviz.Digraph()

    # Initialize nodes
    # - key nodes are red,
    # - dominated nodes are red
    #   - frontier nodes are dotted
    # - rest are black
    for node in tree_nodes:
        color = "black"
        if node == key_node:
            color = "blue"
        elif key_node in doms[node] or node in frontier:
            color = "red"

        g.node(
            node.id,
            briltxt.instr_to_string(node.instr)
            if "op" in node.instr
            else f"LABEL <{node.instr.get('label')}>",  # must be label
            color=color,
            style="dotted" if node in frontier else "",
        )

    # key: node id
    # value: 0 = unvisited, -1 = visiting, 1 = visited
    visit_state: Dict[str, int] = {node.id: 0 for node in tree_nodes}

    q: deque[Node] = deque(tree_nodes)

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

    return g.source


if __name__ == "__main__":
    program, cli_flags = load(["-t", "-f", "-v"])

    if program is None:
        sys.exit(1)

    if not cli_flags["t"] and not cli_flags["f"]:
        print("Please specify either -t or -f")
        sys.exit(1)

    cfg_nodes = to_cfg_fine_grain(program)
    entry_nodes = get_entry_nodes(cfg_nodes)
    doms = _get_dominators(entry_nodes[0])  # TODO: pick the first function (for now)

    if cli_flags["t"]:
        print("Generating dominance tree...")
        t = dominance_tree(doms)
        print(visualize(t, forward=False))

    elif cli_flags["f"]:
        print("Generating dominance frontier for all nodes in CFG...")
        t = dominance_tree(doms)
        frontiers = [dominance_frontier(node) for node in cfg_nodes]

        if not cli_flags["v"]:
            for i in range(len(cfg_nodes)):
                print(f"Node {cfg_nodes[i].id}:")
                print(
                    visualize_frontier(
                        cfg_nodes[i], frontiers[i], doms, cfg_nodes, False
                    )
                )
        else:
            # visualize animation for dominance relation for all nodes in CFG
            name = "perfect"
            dfs = DotFilmStrip(name)
            dfs.extend_frames(
                [
                    visualize_frontier(
                        cfg_nodes[i], frontiers[i], doms, cfg_nodes, False
                    )
                    for i in range(len(cfg_nodes))
                ]
            )
            dfs.render(f"./lesson_tasks/l5/dom-animations/{name}")
