import sys
from collections import defaultdict
from typing import Dict, Iterable, List, Set

from bril_type import *
from cfg import cfg_visualize, to_cfg_fine_grain
from dfa_framework import DataFlowAnalysis
from node import Node
from utils import load


def reaching_definition(cfg_root_nodes: List[Node]) -> None:
    """Compute and reaching definitions for each instruction in the program."""

    def transfer_function(node: Node, in_set: Set) -> Set:
        """New defintions in node, plus definitions that reach the node, minus definitions that are killed in the node."""
        return in_set | set(node.instr.get("dest", []))

    def merge_function(sets: Iterable[Set]) -> Set:
        merge_set = set()
        for s in sets:
            merge_set |= s
        return merge_set

    init_in_set: Dict[str, Set] = defaultdict(set)
    init_out_set: Dict[str, Set] = defaultdict(set)

    for root_node in cfg_root_nodes:
        dfa = DataFlowAnalysis(
            entry_node=root_node,
            in_sets=init_in_set,
            out_sets=init_out_set,
            transfer_function=transfer_function,
            merge_function=merge_function,
        )
        dfa.run()


def get_root_nodes(cfg_nodes: List[Node]) -> List[Node]:
    return [node for node in cfg_nodes if len(node.predecessors) == 0]


if __name__ == "__main__":
    program: Program = load()

    if program is None:
        sys.exit(1)

    cfgs = to_cfg_fine_grain(program)
    cfg_visualize(cfgs)

    reaching_definition(get_root_nodes(cfgs))
    # json.dump(program, sys.stdout, indent=2)
