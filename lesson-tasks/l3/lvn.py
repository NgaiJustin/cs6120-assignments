import sys
import json

from bril_type import Instruction
from blocks import Block, func_to_blocks
from collections import defaultdict
from typing import Dict, List
from utils import load, flatten


def lvn(block: Block) -> tuple[Block, int]:
    table: Dict[tuple, str] = defaultdict(str)  # Maps value tuples to canonical vars
    var2num: Dict[str, int] = defaultdict(int)  # Maps var names to their row number
    num2val: List[tuple] = []  # Maps row entry number to value tuple

    # Maps instruction indices to var names (to take ID from)
    to_replace: Dict[int, str] = defaultdict(dict)

    def instr_to_tuple(instr: Instruction) -> tuple:
        # TODO: Add canonicalization of the tuple (e.g., sort args)
        # (add, 1, 2) == (add, 2, 1)

        value = [instr.op]
        for arg in instr.get("args", []):
            value.append(var2num[arg])
        return tuple(value)

    def get_dest_replaced_arr():
        """Pre-compute if an instr at i will be overwritten later"""
        dest_replaced_arr = [False] * len(block)
        vars_so_far = set()
        for ii in range(len(block) - 1, -1, -1):
            instr = block[ii]
            dest_replaced_arr[ii] = "dest" in instr and instr["dest"] in vars_so_far
        return dest_replaced_arr

    dest_will_be_replaced = get_dest_replaced_arr()

    curr_num = 0
    for ii, instr in enumerate(block):
        value = instr_to_tuple(instr)

        if value in table:
            # The value has been computed before; reuse it.
            var = table[value]
            to_replace[ii] = var

        else:
            # A newly computed value.
            dest = instr.dest

            if dest_will_be_replaced[ii]:
                dest = f"{dest}{curr_num}"
                instr["dest"] = dest
            else:
                dest = instr["dest"]

            table[value] = dest
            var2num[dest] = curr_num

            for ai, arg in enumerate(instr.get("args", [])):
                instr["args"][ai] = table[var2num[arg]]

            curr_num += 1


if __name__ == "__main__":
    program = load()

    if program is None:
        sys.exit(1)

    # LVN pass

    json.dump(program, sys.stdout, indent=2)
