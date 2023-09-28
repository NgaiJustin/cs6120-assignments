from typing import Dict, List

from bril_type import *
from node import RootNode, Node, visualize
from utils import load


def to_cfg_fine_grain(bril: Program) -> List[RootNode]:
    """
    Convert a Bril program to a list control flow graph (one graph for each function)

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
    program, cli_flags = load()

    for root_node in to_cfg_fine_grain(program):
        print(visualize(root_node.entry_node))
