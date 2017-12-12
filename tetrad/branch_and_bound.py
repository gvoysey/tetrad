"""Prune a tree of tetrads via maximum parsimony branch and bound"""
import sys
import os
import anytree
import attr
from anytree import Node
from typing import Iterable
from tetrad.tree_io import read_tree, extract_tetrads_to_csv, cumulative_cost
from tetrad.base import data_path


def compute_cumulative_cost(node: Node):
    node.cumulative_cost = cumulative_cost(node)
    # history[' '.join(node.name)] = node


def add_incumbent(node: Node):
    pass
    # incumbents[' '.join(node.name)] = node


def find_min(nodes: Iterable[Node]):
    node_list = [n for n in nodes if not n.is_root]
    for x in node_list:
        if not has_cumulative_cost(x):
            compute_cumulative_cost(x)

    return min(node_list, key=lambda x: x.cumulative_cost)


def visited(node: Node):
    return hasattr(node, 'visited')


def has_cumulative_cost(node: Node):
    return hasattr(node, 'cumulative_cost')


def visit(node: Node):
    node.visited = True
    return node


def find_candidate_minima(node: Node):
    """find everyone above this node that we've already visited.
    Previously visited nodes have a cumulative cost."""
    touched = anytree.findall(node.root, filter_=lambda x: x.depth < node.depth and not x.is_root and not visited(x))
    # and visited(x))  # and hasattr(x, 'cumulative_cost'))
    return touched


@attr.s
class BranchBound:
    previous_node = attr.ib(default=None)
    history = attr.ib(default=[])
    incumbent = attr.ib(default=None)
    pruned_count = attr.ib(default=0)
    iter_count = attr.ib(default=0)

    def walk(self, node: Node):
        self.iter_count += 1
        print(f'current node: {node.name}, depth: {node.depth}')
        compute_cumulative_cost(node)
        visit(node)

        if not node.is_leaf:
            print('\tThis is not a leaf; continuing down')
            self.walk(find_min(node.children))
        else:
            print('\tThis is a leaf; checking incumbency.')
            if self.incumbent is None or self.incumbent.cumulative_cost > node.cumulative_cost:
                print(
                    f'\t\tThere is no incumbent yet, or this leaf has a lower cost.  Promoting {node.name} to incumbent.')
                self.incumbent = node
                to_prune = anytree.findall(node.root, filter_=lambda x: not x.is_root
                                                                        and x.depth < node.depth
                                                                        and has_cumulative_cost(x)
                                                                        and x.cumulative_cost > node.cumulative_cost)
                for x in to_prune:
                    x.parent = None
                pruned = len(to_prune)
                print(f'\t\tPruned {pruned} nodes')
                self.pruned_count += pruned
                self.history.append(node)
                next_node = find_min([x for x in node.root.children if not visited(x)])
                print(f'\t\tIdentified new minimum node to visit: {next_node.name}, depth {next_node.depth}')
                self.walk(next_node)
            else:
                candidate_minima = [x for x in node.root.children if not visited(x) and x not in node.ancestors]
                if candidate_minima:
                    next_node = find_min(candidate_minima)
                    print(f"\t\tLeaf {node.name} has a larger cumulatuve cost than the current incumbent.")
                    print(f'\t\tReturning to a higher node {next_node.name}')
                    self.walk(next_node)
                else:
                    print(
                        f'\t\t\tTree is depleted. This leaf is not the new incumbent but no higher nodes have a lower cumulative cost')
                    print(f'Pruning complete. {self.pruned_count} nodes were removed in {self.iter_count} passes')
                    return node.root


def main(tree_path: str):
    tree = read_tree(tree_path)
    size = len(tree.root.descendants)
    tree = BranchBound().walk(tree)
    pruned_size = len(tree.root.descendants)
    extract_tetrads_to_csv(tree, 'branched_and_bound.csv')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tree_file = sys.argv[1]
        print(f'Using new tree {tree_file}')
    else:
        tree_file = os.path.join(data_path, 'full_tree.json')
        print(f'Using previously generated tree {tree_file}')
    main(tree_file)
