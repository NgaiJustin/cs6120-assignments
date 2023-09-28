"""
A series of utility functions for transforming BRIL programs into and out of SSA form.
"""
import sys
from collections import defaultdict, deque
from typing import Dict, List, Set

from bril_type import *
from cfg import get_entry_nodes, to_cfg_fine_grain
from dominator import dominance_frontier
from node import Node, PhiNode, visualize
from utils import load


def _collect_vars(entry_node: Node) -> Dict[str, Set[Node]]:
    """
    Return a mapping of variables to the nodes in which they are defined/assigned .
    """
    var_to_assignments: Dict[str, Set[Node]] = defaultdict(set)
    q = deque([entry_node])
    seen: Set[str] = set()
    while q:
        node = q.popleft()
        seen.add(node.id)

        # assignment statement
        if "dest" in node.instr:
            var_name = node.instr["dest"]
            var_to_assignments[var_name].add(node)

        q.extend([succ for succ in node.successors if succ.id not in seen])

    return var_to_assignments


def _rename_vars(node: Node) -> None:
    pass


def to_ssa(entry_node: Node) -> None:
    """
    Convert a CFG into SSA form.
    """
    var_to_assignments = _collect_vars(entry_node)

    for var in var_to_assignments.keys():
        assignments_q = deque(var_to_assignments[var])
        while assignments_q:
            node = assignments_q.popleft()
            for df_node in dominance_frontier(node, entry_node):
                # add phi node to df_node
                if df_node.phi_node is None:
                    df_node.phi_node = PhiNode()
                df_node.phi_node.add_var(var, node.id, var)

                # update assignments to include the phi node use case
                if df_node not in var_to_assignments[var]:
                    var_to_assignments[var].add(df_node)
                    assignments_q.append(df_node)

    # traverse all nodes and rename variables
    q = deque([entry_node])
    seen: Set[str] = set()

    while q:
        curr_node = q.popleft()
        _rename_vars(curr_node)
        seen.add(curr_node.id)
        q.extend([succ for succ in curr_node.successors if succ.id not in seen])


def from_ssa(cfg_nodes: List[Node]) -> List[Node]:
    """
    Convert a CFG from SSA form back into regular form.
    """
    return []


def validate_ssa(cfg_nodes: List[Node]) -> bool:
    """
    Validate that a CFG is in SSA form.
    """
    return True


if __name__ == "__main__":
    program, cli_flags = load(["-to", "-from", "-check"])

    if program is None:
        sys.exit(1)

    if not cli_flags["to"] and not cli_flags["from"]:
        print("Please specify either: \n  ... ssa.py -to \n  ... ssa.py -from")
        sys.exit(1)

    cfg_root_nodes = to_cfg_fine_grain(program)

    if cli_flags["to"]:
        for root_node in cfg_root_nodes:
            to_ssa(root_node.entry_node)
            print(visualize(root_node.entry_node))

    elif cli_flags["from"]:
        if cli_flags["-check"]:
            # Validate that the program is in SSA form
            pass
        pass
