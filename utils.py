"""Utility functions for working with Bril programs"""

import argparse
import json
import sys
from typing import Dict, List, Tuple

from bril_type import *


def load(cli_flags: List[str] = []) -> Tuple[Program, Dict]:
    """Load a .bril program from the command line or stdin, expecting the specified cli_flags"""

    parser = argparse.ArgumentParser(exit_on_error=True)
    for cli_flag in cli_flags:
        parser.add_argument(cli_flag)
    args = parser.parse_args()

    try:
        return (json.load(sys.stdin), vars(args))
    except json.JSONDecodeError:
        print("Invalid JSON")
        return (Program(functions=[]), vars(args))


def flatten(blocks: list[list[Instruction]]):
    """Flatten a list of basic blocks into a single list of instructions."""
    return [instr for block in blocks for instr in block]
