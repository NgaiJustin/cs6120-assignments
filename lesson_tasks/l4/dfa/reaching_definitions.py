import sys
import json

from ...utils.bril_type import *
from ..cfg import to_cfg_fine_grain, cfg_visualize
from ...utils.utils import load


def reaching_definition(program):
    """Compute and reaching definitions for each instruction in the program."""


if __name__ == "__main__":
    print("smd")
    program: Program = load()

    if program is None:
        sys.exit(1)

    cfgs = to_cfg_fine_grain(program)
    cfg_visualize(cfgs[0])

    json.dump(program, sys.stdout, indent=2)
