from node import Node
from collections import deque
from dataclasses import dataclass

from typing import Callable, Dict, Iterable, List


@dataclass(frozen=True)
class DataFlowAnalysis:
    entry_node: Node
    in_sets: Dict[str, set]
    out_sets: Dict[str, set]
    transfer_function: Callable[[Node, set], set]
    merge_function: Callable[[Iterable[set]], set]

    def run(self: "DataFlowAnalysis") -> None:
        # Implement worklist algorithm with an initial DFS pass
        worklist: deque[Node] = deque([self.entry_node])
        iters = 0

        while worklist:
            node = worklist.popleft()

            in_set = self.in_sets[node.id]
            out_set = self.out_sets[node.id]

            new_in_set = self.merge_function(
                [self.out_sets[pred.id] for pred in node.predecessors]
            )
            new_out_set = self.transfer_function(node, in_set)

            if new_in_set != in_set or new_out_set != out_set:
                self.in_sets[node.id] = new_in_set
                self.out_sets[node.id] = new_out_set
                worklist.extend(node.successors)

            iters += 1

        print(f"Ran {iters} iterations")
