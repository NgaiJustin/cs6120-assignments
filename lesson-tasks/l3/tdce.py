# Write a program that loads a json file from the command line and prints it to the console.

import sys
import argparse
import json

from collections import defaultdict
from blocks import func_to_blocks
from typing import Dict
from bril_type import *


def flatten(blocks: list[list[Instruction]]):
    """Flatten a list of basic blocks into a single list of instructions."""
    return [instr for block in blocks for instr in block]


def tdce(blocks: list[list[Instruction]]):
    """Perform dead code elimination on a list of basic blocks."""
    to_delete = defaultdict(
        set
    )  # Map of block indices to instruction indices to delete

    for bi, block in enumerate(blocks):
        last_def: Dict[str, int] = {}  # Map of variable names to index of last def

        for ii, instr in enumerate(block):
            # Check for uses
            for arg in instr.get("args", []):
                last_def.pop(arg, None)  # Remove defs that are used

            # Check for defs
            if "dest" in instr:
                if instr["dest"] in last_def:
                    # Previous def is dead
                    to_delete[bi].add(last_def[instr["dest"]])

                last_def[instr["dest"]] = ii

        # If last_def is not empty, then flag all of the entries for deletion
        if last_def:
            for ii in last_def.values():
                to_delete[bi].add(ii)

    # Batch delete dead instructions
    for bi, to_delete_instrs_i in to_delete.items():
        blocks[bi] = [
            instr for ii, instr in enumerate(blocks[bi]) if ii not in to_delete_instrs_i
        ]

    return blocks


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


if __name__ == "__main__":
    program = load()
    if program:
        for fi, func in enumerate(program["functions"]):
            basic_blocks = func_to_blocks(func)
            new_instrs = tdce(basic_blocks)
            program["functions"][fi]["instrs"] = flatten(new_instrs)

            # TODO: Measure the performance of dead code elimination

    json.dump(program, sys.stdout, indent=2)
