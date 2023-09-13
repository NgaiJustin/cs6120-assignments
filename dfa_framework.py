from node import Node
from collections import deque


class DataFlowAnalysis:
    def __init__(
        self,
        cfg,
        init_sets=None,
        transfer_function=None,
        merge_function=None,
    ):
        self.cfg = cfg
        self.in_sets = {}
        self.out_sets = {}
        self.transfer_function = {}
        self.merge_function = {}
        self.init_sets()

    def init_sets(self):
        for node in self.cfg.nodes:
            self.in_sets[node] = set()
            self.out_sets[node] = set()
            self.transfer_function[node] = lambda in_set: in_set
            self.merge_function[node] = lambda in_sets: set.union(*in_sets)

    def run(self):
        # Implement worklist algorithm with an initial DFS pass
        worklist = deque()
        changed = True
        while changed:
            changed = False
            for node in self.cfg.nodes:
                in_set = self.in_sets[node]
                out_set = self.out_sets[node]
                transfer_function = self.transfer_function[node]
                merge_function = self.merge_function[node]

                new_in_set = merge_function(
                    [self.out_sets[pred] for pred in self.cfg.predecessors(node)]
                )
                new_out_set = transfer_function(in_set, node)

                if new_in_set != in_set or new_out_set != out_set:
                    changed = True
                    self.in_sets[node] = new_in_set
                    self.out_sets[node] = new_out_set

    def get_in_set(self, node: Node):
        return self.in_sets[node]

    def get_out_set(self, node: Node):
        return self.out_sets[node]
