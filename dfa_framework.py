from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, Generic, Iterable, Set, TypeVar, List

from node import Node

import graphviz  # type: ignore

T = TypeVar("T")


class DataFlowAnalysis(Generic[T]):
    entry_node: Node
    in_sets: Dict[str, T]
    out_sets: Dict[str, T]
    transfer_function: Callable[[Node, T], T]
    merge_function: Callable[[List[T]], T]

    visualize_mode: bool  # If true, track vizualized dot graph of each iter
    dot_graphs: List[str] = []  # List of dot graphs for each iter

    def __init__(
        self: "DataFlowAnalysis",
        entry_node: Node,
        in_sets: Dict[str, T],
        out_sets: Dict[str, T],
        transfer_function: Callable[[Node, T], T],
        merge_function: Callable[[List[T]], T],
        visualize_mode: bool = False,
    ) -> None:
        self.entry_node = entry_node
        self.in_sets = in_sets
        self.out_sets = out_sets
        self.transfer_function = transfer_function
        self.merge_function = merge_function
        self.visualize_mode = visualize_mode

    def run(self: "DataFlowAnalysis") -> None:
        # Init worklist with all nodes in CFG
        seen: Set[str] = set()
        q: deque[Node] = deque([self.entry_node])
        worklist: deque[Node] = deque()
        while q:
            node = q.popleft()
            if node.id not in seen:
                seen.add(node.id)
                worklist.append(node)
                for succ in node.successors:
                    q.append(succ)

        iters = 0
        while worklist:
            node = worklist.popleft()

            in_set: T = self.in_sets[node.id]
            out_set: T = self.out_sets[node.id]

            new_in_set: T = self.merge_function(
                [self.out_sets[pred.id] for pred in node.predecessors]
            )
            new_out_set: T = self.transfer_function(node, in_set)

            if new_in_set != in_set or new_out_set != out_set:
                # print("DEBUG", new_in_set, in_set)
                # print("DEBUG", new_out_set, out_set)
                self.in_sets[node.id] = new_in_set
                self.out_sets[node.id] = new_out_set
                worklist.extend(node.successors)

            iters += 1
            if self.visualize_mode:
                self.dot_graphs.append(self.visualize())

        print(f"Ran {iters} iterations")

    def visualize(self: "DataFlowAnalysis") -> str:
        """Visualize a dataflow analysis on CFG using graphviz.

        Paste output in https://edotor.net/ for a pretty diagram"""
        import briltxt  # type: ignore

        g = graphviz.Digraph()
        g.attr("node", shape="none", width="1in")  # Remove border around nodes

        # init cfg_nodes as all nodes reachable from entry_node
        seen: Set[str] = set()
        q: deque[Node] = deque([self.entry_node])
        cfg_nodes: List[Node] = []
        while q:
            node = q.popleft()
            if node.id not in seen:
                seen.add(node.id)
                cfg_nodes.append(node)
                for succ in node.successors:
                    q.append(succ)

        # init nodes in graphviz
        for node in cfg_nodes:
            node_label = (
                briltxt.instr_to_string(node.instr)
                if "op" in node.instr
                else f"LABEL {node.instr.get('label')}"
            )
            in_set_label = self.in_sets[node.id]
            out_set_label = (
                "~"
                if self.in_sets[node.id] == self.out_sets[node.id]
                else self.out_sets[node.id]
            )
            table_html = f'<<table border="0" cellborder="1" cellspacing="0"><tr><td><b>{in_set_label}</b></td></tr><tr><td>{node_label}</td></tr><tr><td><b>{out_set_label}</b></td></tr></table>>'
            g.node(
                node.id,
                table_html,
            )

        # key: node id
        # value: 0 = unvisited, -1 = visiting, 1 = visited
        visit_state: Dict[str, int] = {node.id: 0 for node in cfg_nodes}

        q = deque(cfg_nodes)

        while len(q) > 0:
            node = q.pop()

            if visit_state[node.id] == 1:  # Already visited
                continue
            elif visit_state[node.id] == -1:  # Loop
                visit_state[node.id] = 1
            else:
                for next_node in node.successors:
                    g.edge(node.id, next_node.id)

                    if visit_state[next_node.id] == 1:
                        q.append(next_node)
                        visit_state[next_node.id] = -1

        # print(g.source)
        return g.source
