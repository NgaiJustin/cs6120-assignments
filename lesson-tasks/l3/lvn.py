import sys
import json

from bril_type import Instruction
from blocks import func_to_blocks
from collections import defaultdict
from typing import Dict
from utils import load, flatten

if __name__ == "__main__":
    program = load()

    if program is None:
        sys.exit(1)

    # TVN pass

    json.dump(program, sys.stdout, indent=2)
