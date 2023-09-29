"""
A series of utility functions for transforming BRIL programs into and out of SSA form.
"""
import json
import sys
from collections import defaultdict, deque
from typing import Dict, List, Set

from block import Block, blocks_to_instrs
from block import visualize as visualize_block
from bril_type import *
from cfg import to_cfg
from dominator import (
    _get_dominators_block,
    dominance_frontier_block,
    dominance_tree_block,
)
from node import Node, PhiNode
from utils import load


def _collect_vars(entry_node: Block) -> Dict[str, Set[Block]]:
    """
    Return a mapping of variables to the nodes in which they are defined/assigned .
    """
    var_to_assignments: Dict[str, Set[Block]] = defaultdict(set)
    q = deque([entry_node])
    seen: Set[str] = set()
    while q:
        block = q.popleft()
        seen.add(block.id)

        for instr in block.instrs:
            # assignment statement
            if "dest" in instr:
                var_name = instr["dest"]
                var_to_assignments[var_name].add(block)

        q.extend([succ for succ in block.successors if succ.id not in seen])

    return var_to_assignments


def _rename_vars(entry_node: Block, dom_tree_dict: Dict[str, List[Block]]) -> None:
    """
    Rename variables in a CFG to be in SSA form.
    - entry_node: the entry node of the CFG
    - dom_tree_dict: a mapping of node_id to nodes that it immediately dominates
    """
    # key: old_var_name, value: deque of renamed var_names (var -> var_0, var_1, etc.)
    var_stack: Dict[str, deque] = defaultdict(deque)

    # could use len(var_stack[var]) instead?
    var_counter: Dict[str, int] = defaultdict(int)

    # tracks the current path the recursive _rename function has taken from the entry_block
    # node_ids_seen: Set[str] = set()

    def _get_new_name(var: str) -> str:
        new_name = f"{var}_{var_counter[var]}"
        var_counter[var] += 1
        var_stack[var].append(new_name)
        return new_name

    def _rename(block: Block) -> None:
        # node_ids_seen_cache = node_ids_seen.copy()
        # node_ids_seen.add(block.id)

        # deep copy of var_stack
        var_stack_cache = {var_name: q.copy() for var_name, q in var_stack.items()}

        # rename dest for all phi_nodes in current node
        if block.phi_nodes is not None:
            for _, phi in block.phi_nodes.items():
                phi.dest = _get_new_name(phi.dest)

        for instr in block.instrs:
            if "args" in instr:
                # replace args
                new_args = [
                    var_stack[arg][-1] for arg in instr["args"] if arg in var_stack
                ]
                instr["args"] = new_args

            if "dest" in instr:
                # replace dest
                pre_rename_dest = instr["dest"]
                post_rename_dest = _get_new_name(pre_rename_dest)
                instr["dest"] = post_rename_dest

        # update phi_nodes in successors
        for succ in block.successors:
            if succ.phi_nodes is not None:
                for pre_rename_dest, phi in sorted(
                    succ.phi_nodes.items(), key=lambda x: x[0]
                ):
                    # if phi_src_node_id exists on the current path
                    # (recursively traversed from the entry_node)
                    if len(var_stack[pre_rename_dest]) > 0:
                        phi.args[block.label] = var_stack[pre_rename_dest][-1]
                    else:
                        phi.args[block.label] = "?"

        # rename all immediately dominated nodes
        for im_dom_node in sorted(dom_tree_dict[block.id]):
            _rename(im_dom_node)

        # restore var_stack
        var_stack.clear()
        var_stack.update(var_stack_cache)

        # # restore node_ids_seen
        # node_ids_seen.clear()
        # node_ids_seen.update(node_ids_seen_cache)

    _rename(entry_node)


def to_ssa(entry_block: Block, dest_to_types: Dict[str, Type]) -> List[Instruction]:
    """
    Convert a CFG into SSA form.
    """
    var_to_assignments = _collect_vars(entry_block)

    for var in var_to_assignments.keys():
        assignments_q = deque(var_to_assignments[var])
        while assignments_q:
            block = assignments_q.popleft()
            for df_block in dominance_frontier_block(block, entry_block):
                # no phi_nodes, create one for var
                if df_block.phi_nodes is None:
                    df_block.phi_nodes = {}

                # no phi_node for var, create one
                if var not in df_block.phi_nodes:
                    df_block.phi_nodes[var] = PhiNode(dest=var, args={})

                # different assignment to var, add to phi_node
                if (
                    block.label not in df_block.phi_nodes[var].args
                    and df_block.id != block.id
                ):
                    df_block.phi_nodes[var].args[block.label] = var

                # update assignments to include the phi node use case
                if df_block not in var_to_assignments[var]:
                    var_to_assignments[var].add(df_block)
                    assignments_q.append(df_block)

    doms = _get_dominators_block(entry_block)
    all_blocks = {block.id: block for block in doms.keys()}

    dom_tree = dominance_tree_block(doms)
    dom_tree_dict = {
        block.id: [all_blocks[succ.id] for succ in block.successors]
        for block in dom_tree
    }

    _rename_vars(entry_block, dom_tree_dict)

    # add phi nodes to block.instrs
    for block in blocks:
        if block.phi_nodes is not None:
            for pre_rename_var, phi in block.phi_nodes.items():
                block.instrs.insert(
                    1,  # after label
                    {
                        "op": "phi",
                        "dest": phi.dest,
                        "type": dest_to_types[pre_rename_var],  # TODO: fix later
                        "labels": [label for label in phi.args.keys()],
                        "args": [renamed_var for renamed_var in phi.args.values()],
                    },
                )
            block.phi_nodes = None

    return blocks_to_instrs(blocks)


def from_ssa(cfg_nodes: List[Node]) -> List[Node]:
    """
    Convert a CFG from SSA form back into regular form.
    """
    return []


def validate_ssa(cfg_nodes: List[Node]) -> bool:
    """
    Validate that a CFG is in SSA form.
    """
    return True


if __name__ == "__main__":
    program, cli_flags = load(["-to", "-from", "-check", "-v"])

    if program is None:
        sys.exit(1)

    if not cli_flags["to"] and not cli_flags["from"]:
        print("Please specify either: \n  ... ssa.py -to \n  ... ssa.py -from")
        sys.exit(1)

    if cli_flags["to"]:
        for fi, func in enumerate(program["functions"]):
            blocks = to_cfg(func.get("instrs", []), fi)
            entry_block = blocks[0]
            # get types of all variables in preparation for phi node construction
            dest_to_types: Dict[str, Type] = {}
            for block in blocks:
                for instr in block.instrs:
                    if "dest" in instr and "type" in instr:
                        dest_to_types[instr["dest"]] = instr["type"]

            # mutate func
            func["instrs"] = to_ssa(entry_block, dest_to_types)

            if cli_flags["v"]:
                print(visualize_block(blocks))

        if not cli_flags["v"]:
            print(json.dumps(program, indent=2, sort_keys=True))

    elif cli_flags["from"]:
        if cli_flags["-check"]:
            # Validate that the program is in SSA form
            pass
        pass
