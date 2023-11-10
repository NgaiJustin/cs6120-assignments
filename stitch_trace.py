"""
This module stitches the speculative execution into a Bril program based on a trace of the 
program's execution.

A trace can be produced by feeding a Bril program through `brili-trace` instead of `brili`. 
"""
import argparse
import json
import sys
from typing import List

from block import Block, blocks_to_instrs
from bril_type import *
from cfg import to_cfg
from utils import flatten


def stitch_trace(blocks: List[Block], trace_instrs: List[Instruction]) -> List[Block]:
    """
    Stitch a trace into a CFG.
    """
    for block in blocks:
        try:
            insert_idx = next(
                i for i, v in enumerate(block.instrs) if v.get("label") == "entry"
            )
            insert_idx += 1
            block.instrs.insert(insert_idx, {"op": "speculate"})
            for instr in trace_instrs:
                insert_idx += 1
                block.instrs.insert(insert_idx, instr)
            block.instrs.insert(insert_idx + 1, {"op": "commit"})
            block.instrs.insert(
                insert_idx + 2,
                {"args": [], "op": "ret"},
            )
            block.instrs.insert(insert_idx + 3, {"label": "failed"})
        except StopIteration:
            pass

    return blocks


if __name__ == "__main__":
    # parse program from stdin
    # parse trace file from -t

    parser = argparse.ArgumentParser(exit_on_error=True)
    parser.add_argument("-t", type=str, help="path to trace file")
    args = parser.parse_args()
    cli_flags = vars(args)

    program: Program = Program(functions=[])

    try:
        program = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Invalid JSON")
        sys.exit(1)

    if not cli_flags["t"]:
        print("Please specify -t trace")
        sys.exit(1)

    trace_file_path = cli_flags["t"]
    trace_instr_strs: List[str] = []

    with open(trace_file_path) as file:
        trace_instr = json.load(file)

    trace_instr_map = {"main": trace_instr[0]}  # type: ignore
    trace_instr_map["main"] = [
        i
        for i in trace_instr_map["main"]
        if i.get("op") != "br" and i.get("op") != "jmp"
    ]

    # stitch trace into program
    for func in program["functions"]:
        if func.get("name") == "main":
            blocks = to_cfg(func["instrs"], 0)  # type: ignore

            # operate on blocks
            stitch_trace(blocks, trace_instr_map["main"])

            func["instrs"] = blocks_to_instrs(blocks)

    json.dump(program, sys.stdout, indent=2)
