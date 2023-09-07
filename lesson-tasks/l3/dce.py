# Write a program that loads a json file from the command line and prints it to the console.

import sys
import argparse
import json

from collections import defaultdict
from blocks import func_to_blocks, pprint_blocks
from bril_type import *


def dead_code_elimination(blocks: list[list[Instruction]]):
    """Perform dead code elimination on a list of basic blocks."""
    to_delete = defaultdict(
        set
    )  # Map of block indices to instruction indices to delete

    for bi, block in enumerate(blocks):
        last_def = {}  # Map of variable names to index of last def

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

    # Batch delete dead instructions
    for bi, to_delete_instrs_i in to_delete.items():
        blocks[bi] = [
            instr for ii, instr in enumerate(blocks[bi]) if ii not in to_delete_instrs_i
        ]

    return blocks


def load():
    """Load a .bril program from the command line"""
    if len(sys.argv) < 2:
        print("Provide the Bril program file to load")
        return

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
        for func in program["functions"]:
            basic_blocks = func_to_blocks(func)
            pprint_blocks(basic_blocks)

            # TODO: Measure the performance of dead code elimination
            pprint_blocks(dead_code_elimination(basic_blocks))
