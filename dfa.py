import sys
from typing import List

from bril_type import *
from cfg import cfg_visualize, to_cfg_fine_grain
from dfa_framework import DataFlowAnalysis
from node import Node
from utils import load


def reaching_definition(cfg_nodes: List[Node]) -> DataFlowAnalysis:
    """Compute and reaching definitions for each instruction in the program."""

    dfa = DataFlowAnalysis(cfg_nodes)

    return dfa


if __name__ == "__main__":
    program: Program = load()

    if program is None:
        sys.exit(1)

    cfgs = to_cfg_fine_grain(program)
    cfg_visualize(cfgs)

    # json.dump(program, sys.stdout, indent=2)
