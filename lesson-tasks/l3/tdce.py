# Write a program that loads a json file from the command line and prints it to the console.

import sys
import json

from bril_type import Instruction
from blocks import func_to_blocks
from collections import defaultdict
from typing import Dict
from utils import load, flatten


def tdce(blocks: list[list[Instruction]]) -> tuple[list[list[Instruction]], int]:
    """
    Perform dead code elimination on a list of basic blocks.

    Returns a tuple of the new list of basic blocks and the number of lines eliminated.
    """
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

    lines_eliminated = sum(len(to_delete_i) for to_delete_i in to_delete.values())

    return (blocks, lines_eliminated)


if __name__ == "__main__":
    program = load()

    if program is None:
        sys.exit(1)

    total_lines_eliminated = 0
    while True:
        lines_eliminated = 0
        for fi, func in enumerate(program["functions"]):
            basic_blocks = func_to_blocks(func)
            new_instrs, lines_elim_in_block = tdce(basic_blocks)
            program["functions"][fi]["instrs"] = flatten(new_instrs)

            lines_eliminated += lines_elim_in_block
            # TODO: Measure the performance of dead code elimination

        if lines_eliminated == 0:
            break

    json.dump(program, sys.stdout, indent=2)
