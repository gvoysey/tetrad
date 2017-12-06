"""Prune a tree of tetrads."""
import sys
import os
import anytree
from tetrad.tree_io import read_tree,extract_tetrads_to_csv
from tetrad.base import data_path

history = {}
incumbents = {}


def memoize(node):
    node.cumulative_cost = cumulative_cost(node)
    history[' '.join(node.name)] = node


def add_incumbent(node):
    incumbents[' '.join(node.name)] = node


def cumulative_cost(node):
    prev_cost = sum(x.cost for x in node.ancestors if not x.is_root)
    if not node.is_root:
        return prev_cost + node.cost
    else:
        return None


def find_candidate_minima(node):
    """find everyone above this node that we've already visited. Previously visited nodes have a cumulative cost."""
    touched = anytree.findall(node.root, filter_=lambda x: x.depth <= node.depth and hasattr(x, 'cumulative_cost'))
    return touched


def walk_tree(current_node):
    print(f'current node: {current_node.name}, depth: {current_node.depth}')
    # i have now seen this node; write it down and compute its cumulative cost
    memoize(current_node)
    # find the minimum of  this node's siblings and everything every level up.
    # min_sibling = find_min(current_node.siblings)
    # min_ancestors = []
    # for a in current_node.ancestors:
    #     min_ancestors.append(find_min(a+a.siblings))
    # min_ancestors = find_min(min_ancestors)
    #
    # prev_min = find_min(min_sibling+min_ancestors)
    if current_node.is_root:
        walk_tree(find_min(current_node.children))
    prev_min = find_min(find_candidate_minima(current_node))
    # if we're at the bottom, we might have a new incumbent.
    if current_node.is_leaf:
        add_incumbent(current_node)
        # kill anything whose cumulative sum is higher than this.
        to_prune = anytree.findall(current_node.root,
                                   filter_=lambda node: cumulative_cost(node) > cumulative_cost(current_node))
        for x in to_prune:
            x.parent = None
    else:
        # keep going
        # if my cumulative cost is the min, recurse on my smallest child; otherwise, recurse on the min's smallest child
        if prev_min.cumulative_cost is None or current_node.cumulative_cost < prev_min.cumulative_cost:
            walk_tree(find_min(current_node.children))
        else:
            walk_tree(find_min(prev_min.children))


def find_min(nodes):
    node_list = [n for n in nodes if not n.is_root]
    for x in node_list:
        memoize(x)
    return min(node_list, key=lambda x: cumulative_cost(x))


def main(tree_path):
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
