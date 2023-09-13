import sys
from typing import Iterable, List, Dict, Set

from bril_type import *
from cfg import cfg_visualize, to_cfg_fine_grain
from dfa_framework import DataFlowAnalysis
from node import Node
from utils import load


def reaching_definition(cfg_root_nodes: List[Node]) -> None:
    """Compute and reaching definitions for each instruction in the program."""

    def transfer_function(node: Node, in_set: Set) -> Set:
        return set()

    def merge_function(sets: Iterable[Set]) -> Set:
        return set()

    init_in_set: Dict[str, Set] = {node.id: set() for node in cfg_root_nodes}
    init_out_set: Dict[str, Set] = {node.id: set() for node in cfg_root_nodes}

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
