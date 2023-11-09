"""
This module stitches the speculative execution into a Bril program based on a trace of the 
program's execution.

A trace can be produced by feeding a Bril program through `brili-trace` instead of `brili`. 
"""
import argparse
import json
import sys
from typing import List

from bril_type import *
from utils import load

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
        trace_instr_strs = file.readlines()

    trace_instrs = [Instruction(json.loads(s)) for s in trace_instr_strs]  # type: ignore
    for trace_instr in trace_instrs:
        print(trace_instr)
