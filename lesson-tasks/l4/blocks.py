from bril_type import *
from typing import List

import pprint

TERMINATORS = {"jmp", "br", "ret"}

Block = List[Instruction]


def func_to_blocks(func: Function) -> List[Block]:
    blocks: List[Block] = []
    curr_block: Block = []

    """Convert Bril function into a list of basic blocks."""
    for instr in func.get("instrs", []):
        # If instruction, add to block
        if "op" in instr:
            curr_block.append(instr)

            if instr["op"] in TERMINATORS:
                blocks.append(curr_block)
                curr_block = []

        # Is label, end block if non-empty
        else:
            if curr_block:
                blocks.append(curr_block)

            curr_block = [instr]

    # Add last block, if non-empty
    if curr_block:
        blocks.append(curr_block)

    return blocks


def pprint_blocks(blocks: List[Block]):
    """Pretty print a list of basic blocks. Primarily used for debugging."""
    for block in blocks:
        print("Block:")
        for instr in block:
            pprint.pprint(instr)
        print()


test_input = {
    "functions": [
        {
            "instrs": [
                {"dest": "v1", "op": "const", "type": "int", "value": 1},
                {"dest": "v1", "op": "const", "type": "int", "value": 2},
                {"args": ["v1"], "op": "print"},
            ],
            "name": "main",
        }
    ]
}


if __name__ == "__main__":
    blocks = func_to_blocks(test_input["functions"][0])
    pprint_blocks(blocks)
