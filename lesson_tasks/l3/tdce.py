# Write a program that loads a json file from the command line and prints it to the console.

import json
import sys
from collections import defaultdict
from typing import Dict

from .blocks import Block, func_to_blocks

from utils import flatten, load


def get_globally_used_vars(blocks: list[Block]) -> set[str]:
    """
    Return a set of all variables used in the program.
    """
    used_vars = set()

    for block in blocks:
        for instr in block:
            if "args" in instr:
                used_vars.update(instr["args"])

    return used_vars


def tdce(
    blocks: list[Block],
    globally_used_vars: set[str],
) -> tuple[list[Block], int]:
    """
    Perform dead code elimination on a list of basic blocks.

    Returns a tuple of the new list of basic blocks and the number of lines eliminated.
    """
    to_delete = defaultdict(set)  # Map of block indices to instr indices to delete

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

        # Flag all non-globally used variables as dead
        if last_def:
            for var, ii in last_def.items():
                if var not in globally_used_vars:
                    to_delete[bi].add(ii)

    # Batch delete dead instructions
    for bi, to_delete_instrs_i in to_delete.items():
        blocks[bi] = [
            instr for ii, instr in enumerate(blocks[bi]) if ii not in to_delete_instrs_i
        ]

    lines_eliminated = sum(len(to_delete_i) for to_delete_i in to_delete.values())

    return (blocks, lines_eliminated)


if __name__ == "__main__":
    program, _ = load()

    if program is None:
        sys.exit(1)

    total_lines_eliminated = 0
    while True:
        lines_eliminated = 0
        for fi, func in enumerate(program["functions"]):
            basic_blocks = func_to_blocks(func)
            new_instrs, lines_elim_in_block = tdce(
                basic_blocks, get_globally_used_vars(basic_blocks)
            )
            program["functions"][fi]["instrs"] = flatten(new_instrs)

            lines_eliminated += lines_elim_in_block
            # TODO: Measure the performance of dead code elimination

        if lines_eliminated == 0:
            break

    json.dump(program, sys.stdout, indent=2)
