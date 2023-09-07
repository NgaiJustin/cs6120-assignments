"""Utility functions for working with Bril programs used by both tdce.py and lvn.py."""

import json
import argparse

from bril_type import Instruction


def load():
    """Load a .bril program from the command line or stdin."""

    # If no file is specified, read from stdin
    if len(sys.argv) == 1:
        return json.load(sys.stdin)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "f",
        help="The name of the file to load",
        type=argparse.FileType("r"),
        default=sys.stdin,
    )
    args = parser.parse_args()

    try:
        return json.load(args.f)
    except FileNotFoundError:
        print("File not found")
        return
    except json.JSONDecodeError:
        print("Invalid JSON")
        return


def flatten(blocks: list[list[Instruction]]):
    """Flatten a list of basic blocks into a single list of instructions."""
    return [instr for block in blocks for instr in block]
