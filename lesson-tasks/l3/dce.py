# Write a program that loads a json file from the command line and prints it to the console.

import sys
import argparse
import json


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


def dead_code_elimination(program):
    for func in program.get("functions", []):
        for instr in func.get("instrs", []):
            print(instr)


if __name__ == "__main__":
    program = load()
    if program:
        dead_code_elimination(program)
