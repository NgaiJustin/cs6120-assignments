import json
import sys

from bril_type import *
from utils import load
from cfg import cfg_visualize, to_cfg_fine_grain


def reaching_definition(program):
    """Compute and reaching definitions for each instruction in the program."""


if __name__ == "__main__":
    program: Program = load()

    if program is None:
        sys.exit(1)

    cfgs = to_cfg_fine_grain(program)

    for root_nodes in cfgs:
        print(root_nodes)
    cfg_visualize(cfgs)

    # json.dump(program, sys.stdout, indent=2)
