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
    var_to_assigns: Dict[str, Set[Node]] = defaultdict(set)
    q = deque([entry_node])
    while q:
        node = q.popleft()

        # assignment statement
        if "dest" in node.instr:
            var_name = node.instr["dest"]
            var_to_assigns[var_name].add(node)

        q.extend(node.successors)

    return var_to_assigns


def _rename_vars(node: Node) -> None:
    pass


def to_ssa(entry_node: Node) -> List[Node]:
    """
    Convert a CFG into SSA form.
    """
    var_to_assigns = _collect_vars(entry_node)
    for var in var_to_assigns.keys():
        for node in var_to_assigns[var]:
            for df_node in dominance_frontier(node, entry_node):
                # add phi node to df_node
                if df_node.phi_node is None:
                    df_node.phi_node = PhiNode()
                df_node.phi_node.add_var(var, node.id, var)

                # update assignments to include the phi node use case
                var_to_assigns[var].add(df_node)

    return []


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
    program, cli_flags = load(["-t", "-f", "-v"])

    if program is None:
        sys.exit(1)

    if not cli_flags["t"] and not cli_flags["f"]:
        print("Please specify either -t or -f")
        sys.exit(1)

    cfg_nodes = to_cfg_fine_grain(program)
    entry_nodes = get_entry_nodes(cfg_nodes)

    if cli_flags["to_ssa"]:
        pass

    elif cli_flags["from_ssa"]:
        if cli_flags["-check"]:
            # Validate that the program is in SSA form
            pass
        pass
