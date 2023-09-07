# Write a program that loads a json file from the command line and prints it to the console.

import sys
import argparse
import json


def load():
    if len(sys.argv) < 2:
        print("Provide the Bril program file to load")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("f", help="The name of the file to load")
    args = parser.parse_args()

    try:
        with open(args.f) as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None


def dead_code_elimination(program):
    pass


if __name__ == "__main__":
    program = load()
    # dead_code_elimination(program)
    print(program)
