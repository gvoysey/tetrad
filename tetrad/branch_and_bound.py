"""Prune a tree of tetrads via maximum parsimony branch and bound"""
import sys
import os
import anytree
from anytree import Node
from typing import Iterable
from tetrad.tree_io import read_tree, extract_tetrads_to_csv, cumulative_cost
from tetrad.base import data_path

history = {}
incumbents = {}


def memoize(node:Node):
    node.cumulative_cost = cumulative_cost(node)
    history[' '.join(node.name)] = node


def add_incumbent(node:Node):
    incumbents[' '.join(node.name)] = node


def find_min(nodes:Iterable[Node]):
    node_list = [n for n in nodes if not n.is_root]
    for x in node_list:
        memoize(x)

    return min(node_list, key=lambda x: cumulative_cost(x))


def visited(node:Node):
    return hasattr(node, 'visited')


def visit(node:Node):
    node.visited = True
    return node


def find_candidate_minima(node:Node):
    """find everyone above this node that we've already visited.
    Previously visited nodes have a cumulative cost."""
    touched = anytree.findall(node.root, filter_=lambda x: x.depth < node.depth and not x.is_root and not visited(x))
    # and visited(x))  # and hasattr(x, 'cumulative_cost'))
    return touched


previous_node = None


def walk_tree(current_node:Node):
    print(f'current node: {current_node.name}, depth: {current_node.depth}')
    # i have now seen this node; write it down and compute its cumulative cost
    memoize(current_node)
    visit(current_node)
    previous_node = current_node
    # if i'm the root node, i have no dyad information, so just find my smallest child and go there.
    if current_node.is_root:
        min_root_child = find_min(current_node.children)
        walk_tree(min_root_child)
    # if we're at the bottom, we might have a new incumbent.
    if not current_node.is_leaf:
        # find the minimum of this node's siblings and everything every level up.  If the only thing "up" is root, that's ok.
        ancestors = find_candidate_minima(current_node)
        if ancestors:
            prev_min = find_min((a for a in ancestors if a not in current_node.ancestors))
        else:
            prev_min = current_node.root
        # keep going
        # if my cumulative cost is the min, recurse on my smallest child; otherwise, recurse on the min's smallest child
        if prev_min.is_root or current_node.cumulative_cost <= prev_min.cumulative_cost:
            print(f'\tcurrent node cumulative cost was less than previous minimum, continuing down.')
            current_min_child = find_min((c for c in current_node.children if c not in current_node.ancestors))
            walk_tree(current_min_child)
        else:
            print(f'\tcurrent node cumulative cost was greater than previous minimum, jumping.')
            prev_min_child = find_min((c for c in prev_min.children if c not in current_node.ancestors and not visited(c)))
            walk_tree(prev_min_child)
    else:
        add_incumbent(current_node)
        # kill anything whose cumulative sum is higher than this.
        to_prune = anytree.findall(current_node.root,
                                   filter_=lambda node: cumulative_cost(node) > cumulative_cost(current_node))
        for x in to_prune:
            x.parent = None
        print(f'\tfound incumbent {current_node}, pruned {len(to_prune)} nodes.')


def main(tree_path:str):
    tree = read_tree(tree_path)
    tree = walk_tree(tree)
    extract_tetrads_to_csv(tree, 'branched_and_bound.csv')

    # best_nodes = {}
    # incumbents = {}
    # # as written this will take a minute...
    # _,parents,children,grandchildren,greatgrandchildren = (anytree.LevelOrderGroupIter(tree))
    #
    #
    # for idx, level_nodes in enumerate(anytree.LevelOrderGroupIter(tree)):
    #     if idx == 0:
    #         pass
    #     level_min = find_min(level_nodes)
    #
    #
    #
    # min_parent = find_min(parents)
    # min_child = find_min(children)
    # min_grandchild = find_min(grandchildren)
    # min_greatgrandchild = find_min(greatgrandchildren)
    #
    # min_cost = min(min_parent, min_child, min_grandchild, min_greatgrandchild)
    #
    # for child in min_parent.children:
    #     if child.cost <= min_parent.cost + min(parents+min_parent.children):
    #
    #
    #
    #
    #
    # # for i, children in enumerate(anytree.LevelOrderGroupIter(tree)):
    # #     if i==0:
    # #         # nobody cares about the root node.
    # #         pass
    # #     else:
    # #         min_child = min(children, key = lambda  x: x.cost)
    # #         best_nodes[frozenset(min_child.name)] = min_child.cost
    # #         if min_child.cost < min(best_nodes.values()):
    # #             print('found smaller')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.path.join(data_path, 'full_tree.json'))
