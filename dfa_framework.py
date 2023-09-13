from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, Generic, Iterable, Set, TypeVar

from node import Node

T = TypeVar("T")


@dataclass(frozen=True)
class DataFlowAnalysis(Generic[T]):
    entry_node: Node
    in_sets: Dict[str, T]
    out_sets: Dict[str, T]
    transfer_function: Callable[[Node, T], T]
    merge_function: Callable[[Iterable[T]], T]

    def run(self: "DataFlowAnalysis") -> None:
        # Init worklist with all nodes in CFG
        seen: Set[str] = set()
        q: deque[Node] = deque([self.entry_node])
        worklist: deque[Node] = deque()
        while q:
            node = q.popleft()
            worklist.append(node)
            for succ in node.successors:
                if succ.id not in seen:
                    seen.add(succ.id)
                    q.append(succ)
                    worklist.append(succ)

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
