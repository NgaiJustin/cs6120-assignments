from typing import Dict, List

from bril_type import *
from node import RootNode, Node, visualize as visualize_node
from block import Block, visualize as visualize_block
from utils import load


def to_cfg(instrs: List[Instruction], f_id: int) -> List[Block]:
    blocks: List[Block] = []
    block_instrs: List[Instruction] = []

    # Group by basic blocks
    for instr in instrs:
        block_instrs.append(instr)
        if instr.get("op") in {"jmp", "br", "ret"}:
            blocks.append(
                Block(
                    id=f"f{f_id}-{len(blocks)}",
                    label="",
                    predecessors=set(),
                    successors=set(),
                    instrs=block_instrs,
                )
            )
            block_instrs = []

    if block_instrs:
        blocks.append(
            Block(
                id=f"f{f_id}-{len(blocks)}",
                label="",
                predecessors=set(),
                successors=set(),
                instrs=block_instrs,
            )
        )

    # Update labels
    label_to_block = {}
    for block in blocks:
        if "label" in block.instrs[0]:
            block.label = block.instrs[0]["label"]
            label_to_block[block.label] = block
        else:
            block.label = block.id

    # Add edges
    for i in range(len(blocks) - 1):
        if blocks[i].instrs[-1].get("op") in {"jmp", "br"}:
            continue
        blocks[i].successors.add(blocks[i + 1])
        blocks[i + 1].predecessors.add(blocks[i])

    # Add edges for jmp, br
    for block in blocks:
        if block.instrs[-1].get("op") == "jmp" and "labels" in block.instrs[-1]:
            dest = block.instrs[-1]["labels"][0]
            block.successors.add(label_to_block[dest])
            label_to_block[dest].predecessors.add(block)

        elif block.instrs[-1].get("op") == "br" and "labels" in block.instrs[-1]:
            dest_a, dest_b = block.instrs[-1]["labels"]

            block.successors.add(label_to_block[dest_a])
            label_to_block[dest_a].predecessors.add(block)

            block.successors.add(label_to_block[dest_b])
            label_to_block[dest_b].predecessors.add(block)

    return blocks


def to_cfg_fine_grain(bril: Program) -> List[RootNode]:
    """
    Convert a Bril program into control flow graph (one graph for each function) where each
    basic block is a single instruction.

    Returns a RootNode for each function in the program.
    """
    cfg_root_nodes = []
    for fi, func in enumerate(bril["functions"]):
        nodes: List[Node] = []
        labels: Dict[str, Node] = {}

        # Split each instruction into its own basic block
        for ii, instr in enumerate(func.get("instrs", [])):
            node = Node(
                id=f"f{fi}-{ii}",
                predecessors=set(),
                successors=set(),
                instr=instr,
                label=instr.get("label"),
            )
            if node.label is not None:
                labels[node.label] = node

            nodes.append(node)

            if ii == 0:
                # First instruction in a function is the entry node
                cfg_root_nodes.append(
                    RootNode(
                        func_name=func.get("name", f"f{fi}"),
                        func_args=func.get("args", []),
                        func_type=func.get("type", None),
                        entry_node=node,
                    )
                )

        # Add edges between nodes
        for i in range(len(nodes) - 1):
            if nodes[i].instr.get("op") in {"jmp", "br"}:
                continue
            nodes[i].successors.add(nodes[i + 1])
            nodes[i + 1].predecessors.add(nodes[i])

        # Add edges for jmp, br
        for node in nodes:
            # jmp and br instructions have a "labels" field
            # mostly to make type-checker happy
            if "labels" not in node.instr:
                continue

            if node.instr.get("op") == "jmp":
                dest = node.instr["labels"][0]
                node.successors.add(labels[dest])
                labels[dest].predecessors.add(node)

            elif node.instr.get("op") == "br":
                dest_a, dest_b = node.instr["labels"]

                node.successors.add(labels[dest_a])
                labels[dest_a].predecessors.add(node)

                node.successors.add(labels[dest_b])
                labels[dest_b].predecessors.add(node)

    return cfg_root_nodes


def get_entry_nodes(nodes: List[Node]) -> List[Node]:
    """Return the entry nodes (one for each function) of a CFG."""
    return [node for node in nodes if len(node.predecessors) == 0]


if __name__ == "__main__":
    program, cli_flags = load(["-f"])

    if cli_flags["f"]:
        # fine-grain cfg
        for root_node in to_cfg_fine_grain(program):
            print(visualize_node(root_node.entry_node))
    else:
        # basic block cfg
        for fi, func in enumerate(program["functions"]):
            print(f"function {func.get('name', f'f{fi}')}:")
            blocks = to_cfg(func.get("instrs", []), fi)
            print(visualize_block(blocks))
