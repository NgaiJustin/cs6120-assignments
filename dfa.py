import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Set

from bril_type import *
from cfg import cfg_visualize, to_cfg_fine_grain
from dfa_framework import DataFlowAnalysis
from dot import DotFilmStrip
from node import Node
from utils import load


def reaching_definition(
    cfg_root_nodes: List[Node],
    visualize_mode: bool = False,
) -> List[DataFlowAnalysis]:
    """Returns a data flow analysis for reaching defintions for each function in the program.

    Sets contain the names of variables that are defined
    """

    def transfer_function(node: Node, in_set: Iterable[str]) -> Set:
        """New defintions in node, plus definitions that reach the node, minus definitions that are killed in the node."""
        new_set = set(in_set)
        if "dest" in node.instr:
            new_set.add(node.instr["dest"])
        return new_set

    def merge_function(sets: Iterable[Iterable[str]]) -> Iterable:
        merge_set: Set[str] = set()
        for s in sets:
            merge_set |= set(s)
        return merge_set

    init_in_set: Dict[str, Iterable] = defaultdict(set)
    init_out_set: Dict[str, Iterable] = defaultdict(set)

    dfas = []
    for root_node in cfg_root_nodes:
        dfa = DataFlowAnalysis(
            entry_node=root_node,
            in_sets=init_in_set,
            out_sets=init_out_set,
            transfer_function=transfer_function,
            merge_function=merge_function,
            visualize_mode=visualize_mode,
        )
        dfa.run()
        dfas.append(dfa)

    return dfas


def constant_propagation(
    cfg_root_nodes: List[Node],
    visualize_mode: bool = False,
) -> List[DataFlowAnalysis]:
    """Returns a data flow analysis for constant propagation for each function in the program.

    Sets contain a mapping from variable names to their constant values.
    """

    class ConstantType(ABC):
        @abstractmethod
        def merge(self, other: "ConstantType") -> "ConstantType":
            pass

        @abstractmethod
        def val(self) -> Optional[int | bool]:
            pass

    class Constant(ConstantType):
        def __init__(self, val: int | bool):
            self._val = val

        def merge(self, other: "ConstantType") -> "ConstantType":
            if isinstance(other, Constant):
                if self.val() == other.val():
                    return self
                else:
                    return Unknown()
            else:
                return other.merge(self)

        def val(self) -> Optional[int | bool]:
            return self._val

        def __str__(self):
            return str(self._val)

        def __repr__(self):
            return str(self._val)

        def __eq__(self, other):
            if isinstance(other, Constant):
                return self._val == other._val
            else:
                return False

    class Unknown(ConstantType):
        def merge(self, other: "ConstantType") -> "ConstantType":
            return self

        def val(self) -> Optional[int | bool]:
            return None

        def __str__(self):
            return "Unknown"

        def __repr__(self):
            return "Unknown"

        def __eq__(self, other):
            return isinstance(other, Unknown)

    class Uninitialized(ConstantType):
        def merge(self, other: "ConstantType") -> "ConstantType":
            return other

        def val(self) -> Optional[int | bool]:
            return None

        def __str__(self):
            return ""

        def __repr__(self):
            return ""

        def __eq__(self, other):
            return isinstance(other, Uninitialized)

    op_to_func: Dict[str, Callable] = {
        "add": lambda x, y: x + y,
        "mul": lambda x, y: x * y,
        "sub": lambda x, y: x - y,
        "div": lambda x, y: x // y,
        "eq": lambda x, y: x == y,
        "lt": lambda x, y: x < y,
        "gt": lambda x, y: x > y,
        "le": lambda x, y: x <= y,
        "ge": lambda x, y: x >= y,
        "and": lambda x, y: x and y,
        "or": lambda x, y: x or y,
        "not": lambda x: not x,
    }

    def transfer_function(
        node: Node, in_set: Dict[str, ConstantType]
    ) -> Dict[str, ConstantType]:
        """New variables that are constants in this node, plus previous variables that are constants, minus variables that are no longer constants."""
        op = node.instr.get("op")
        if op is None:
            return in_set

        new_mapping = dict(in_set)

        # Assignments of new constant - add to mapping
        if op == "const":
            dest = node.instr.get("dest")
            val = node.instr.get("value")
            if dest is not None and val is not None:
                new_mapping[dest] = Constant(val)

        # Operations with constants - add to mapping
        elif op in op_to_func.keys():
            dest = node.instr.get("dest")
            args = node.instr.get("args")
            if dest is not None and args is not None:
                if len(args) == 2:
                    arg0 = args[0]
                    arg1 = args[1]
                    if arg0 in in_set and arg1 in in_set:
                        new_mapping[dest] = Constant(
                            op_to_func[op](in_set[arg0], in_set[arg1])
                        )
                elif len(args) == 1:
                    arg0 = args[0]
                    if arg0 in in_set:
                        new_mapping[dest] = Constant(op_to_func[op](in_set[arg0]))

        # Override existing constant - set to unknown
        elif "dest" in node.instr:
            dest = node.instr.get("dest")
            if dest in in_set:
                new_mapping[dest] = Unknown()

        return new_mapping

    def merge_function(
        sets: Iterable[Dict[str, ConstantType]]
    ) -> Dict[str, ConstantType]:
        merge_set: Dict[str, ConstantType] = {}
        for s in sets:
            for k, v in s.items():
                if merge_set.get(k) is None:
                    merge_set[k] = v
                else:
                    merge_set[k] = merge_set[k].merge(v)
        return merge_set

    init_in_set: Dict[str, Dict[str, ConstantType]] = defaultdict(defaultdict)
    init_out_set: Dict[str, Dict[str, ConstantType]] = defaultdict(defaultdict)

    dfas = []
    for root_node in cfg_root_nodes:
        dfa = DataFlowAnalysis(
            entry_node=root_node,
            in_sets=init_in_set,
            out_sets=init_out_set,
            transfer_function=transfer_function,
            merge_function=merge_function,
            visualize_mode=visualize_mode,
        )
        dfa.run()
        dfas.append(dfa)

    return dfas


def get_root_nodes(cfg_nodes: List[Node]) -> List[Node]:
    return [node for node in cfg_nodes if len(node.predecessors) == 0]


if __name__ == "__main__":
    program: Program = load()

    if program is None:
        sys.exit(1)

    cfgs = to_cfg_fine_grain(program)

    ####################################################################################
    ## Run reaching definitions DFA on Catalan example and generate DFA animation
    # name = "catalan-reaching-definitons"
    # rd_dfas = reaching_definition(get_root_nodes(cfgs), visualize_mode=True)

    # rd_ex = rd_dfas[1]
    # dfs = DotFilmStrip(name)
    # dfs.dot_frames = rd_ex.dot_graphs
    # dfs.render(f"./lesson_tasks/l4/dfa-animations/{name}")
    ####################################################################################

    ####################################################################################
    ## Run constant prop DFA on Catalan example and generate DFA animation
    name = "catalan-constant-prop"
    cp_dfas = constant_propagation(get_root_nodes(cfgs), visualize_mode=True)

    cp_ex = cp_dfas[1]
    dfs = DotFilmStrip(name)
    dfs.extend_frames(cp_ex.dot_graphs)
    dfs.render(f"./lesson_tasks/l4/dfa-animations/{name}")
    ####################################################################################

    # json.dump(program, sys.stdout, indent=2)
