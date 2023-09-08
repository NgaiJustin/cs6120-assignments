import sys
import json

from bril_type import Instruction
from blocks import Block, func_to_blocks
from collections import defaultdict
from tdce import tdce, get_globally_used_vars
from typing import Dict, List
from utils import load, flatten


def lvn(block: Block):
    """Mutates the block to perform LVN on it."""
    num2val: List[tuple] = []  # Maps row entry number to value tuple
    var2num: Dict[str, int] = {}  # Maps var names to their row number
    num2vars: Dict[
        int, str
    ] = {}  # Maps row numbers to var, note row can point to many vars
    table: Dict[tuple, str] = {}  # Maps value tuples to canonical vars

    # Maps instruction indices to var names (to take ID from)
    to_replace: Dict[int, str] = defaultdict(dict)

    def instr_to_tuple(instr: Instruction) -> tuple:
        # TODO: Add canonicalization of the tuple (e.g., sort args)
        # (add, 1, 2) == (add, 2, 1)
        if "op" not in instr:
            return None

        if instr["op"] == "const":
            return ("const", instr["value"])
        elif instr["op"] == "id":
            return ("id", instr["args"][0])

        value = [instr["op"]]
        if "args" in instr:
            for arg in instr.get("args", []):
                value.append(var2num[arg])

        return tuple(value)

    def get_dest_replaced_arr(block: Block):
        """Pre-compute if an instr at i will be overwritten later"""
        num_instrs = len(block)
        dest_replaced_arr = [False] * num_instrs
        vars_so_far = set()
        for ii in range(num_instrs - 1, -1, -1):
            instr = block[ii]
            if "dest" in instr:
                dest_replaced_arr[ii] = instr["dest"] in vars_so_far
                vars_so_far.add(instr["dest"])
        return dest_replaced_arr

    dest_will_be_replaced = get_dest_replaced_arr(block)

    for ii, instr in enumerate(block):
        if "op" not in instr:
            continue  # Skip labels

        arg_ids = tuple(var2num[var] for var in instr.get("args", []))
        if "args" in instr:
            instr["args"] = [num2vars[n] for n in arg_ids]

        value = instr_to_tuple(instr)

        if value in table:
            # The value has been computed before; reuse it.
            var = table[value]
            to_replace[ii] = var
            var2num[instr["dest"]] = var2num[var]
        else:
            # A newly computed value.
            if "dest" in instr:
                dest = instr["dest"]
                num2val.append(value)
                curr_num = len(num2val) - 1
                var2num[dest] = curr_num

                if dest_will_be_replaced[ii]:
                    dest = f"{dest}_v{curr_num}"
                    instr["dest"] = dest
                else:
                    dest = instr["dest"]

                num2vars[curr_num] = dest
                table[value] = dest
                var2num[dest] = curr_num

                for ai, arg in enumerate(instr.get("args", [])):
                    instr["args"][ai] = table[num2val[var2num[arg]]]

    # Replace all flagged copy propagations
    for ii in range(len(block)):
        if ii in to_replace and "dest" in block[ii]:
            block[ii] = {
                "dest": block[ii]["dest"],
                "op": "id",
                "args": [to_replace[ii]],
            }


if __name__ == "__main__":
    program = load()

    if program is None:
        sys.exit(1)

    for fi, func in enumerate(program["functions"]):
        basic_blocks = func_to_blocks(func)
        new_instrs = []

        for block in basic_blocks:
            block_changed = lvn(block)
            new_instrs.append(block)

        program["functions"][fi]["instrs"] = flatten(new_instrs)

    json.dump(program, sys.stdout, indent=2)
