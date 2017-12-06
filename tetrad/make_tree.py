"""Create a tree of valid tetrads with a cost assigned per node"""
from itertools import permutations, combinations

import numpy as np
import sympy
from anytree import Node
from anytree.exporter import DotExporter, JsonExporter

from tetrad.bio import cost, SURFACE_TARGETS
from datetime import datetime

start = datetime.now()
#  the top level of the tree can be combination-only.
dyad_pairs = list(combinations(SURFACE_TARGETS, 2))
# subsequent levels need a broader search space to account for disorder in pairings.
dyads = list(permutations(SURFACE_TARGETS, 2))
# memoize the costs for efficient lookup.
dyad_costs = {k: cost(k) for k in (frozenset(d) for d in dyad_pairs)}


def get_cost(dyad):
    """Convert a dyad to a frozen set for fast cost lookup in the dyad costs table"""
    return dyad_costs[frozenset(dyad)]


VALID_TETRAD = sympy.Matrix(np.array([[1, 0, 1, 0], [1, 0, 0, 1]
                                     , [0, 1, 1, 0], [0, 1, 0, 1]])).rref()


def is_valid(tetrad):
    """Check if a given input obeys the correct form 
    (a,c), (a,d), (b,c), (b,d).  An input is valid IFF the matrix of states it forms
    is row-equivalent to the known correct state."""

    # list of unique strings in tetrad
    elements = sorted(list(frozenset.union(*tetrad)))
    if len(elements) > 4:
        return False
    tetrad_state = np.zeros((4, 4))
    # the (i,j)th element of tetrad_state is 1 if the ith tetrad pair
    # contains the jth unique string
    for i, pair in enumerate(tetrad):
        for j, e in enumerate(elements):
            if e in pair:
                tetrad_state[i, j] = 1
    return sympy.Matrix(tetrad_state).rref() == VALID_TETRAD


def make_tetrad(*args):
    """makes a frozenset tetrad from a list"""
    return frozenset([frozenset(x) for x in args])


def add_node(dyad, parent_node):
    """Make a cost-scored node from a target pair dyad.  Use memoized cost lookups for speed"""
    matches = [x for x in parent_node.children if x.name == dyad]
    if not any(matches):
        n = Node(dyad)
        n.cost = get_cost(dyad)
        n.parent = parent_node
    else:
        n = matches[0]
    return n


def make_tree():
    """Iteratively build a tree of unique, valid tetrads.  A valid tetrad has 4 target dyads
    whose elements obey the relationship  {(a, c), (a, d), (b, c), (b, d)} """

    # memoized cache of previously-added valid tetrads to prevent duplication.
    valid_tetrads = set()

    root = Node('root')
    root.cost = 0

    # bush_root is A and C
    for parent in dyad_pairs:
        # all children are A and D
        br_children = [d for d in dyads if
                       parent[0] == d[0]  # is a
                       and parent[1] != d[1]]  # is not A.
        for child in br_children:
            # all grandchildren are B and C
            grandchildren = [d for d in dyads if
                             d[0] != parent[0]  # not a
                             and d[0] != child[1]  # not d
                             and d[1] == parent[1]]  # is c

            for grandchild in grandchildren:
                # all greatgrandchildren are B and D
                greatgrandchildren = [d for d in dyads if
                                      d[0] == grandchild[0]
                                      and d[1] == child[1]]

                for greatgrandchild in greatgrandchildren:
                    tetrad = make_tetrad(parent, child, grandchild, greatgrandchild)

                    if is_valid(tetrad) and tetrad not in valid_tetrads:
                        valid_tetrads.add(tetrad)
                        parent_node = add_node(parent, root)
                        child_node = add_node(child, parent_node)
                        grandchild_node = add_node(grandchild, child_node)
                        greatgrandchild_node = add_node(greatgrandchild, grandchild_node)

        print(f'processed bush with root {parent}')

    print(f'took {(datetime.now() -start).total_seconds()} to generate full tree before pruning')
    return root


def main():
    """Make a full tree from the default targets, and export it in graphviz and JSON form."""
    tree = make_tree()
    DotExporter(tree).to_dotfile('full_tree.dot')

    with open('full_tree.json', 'w') as f:
        exporter = JsonExporter(indent=4, sort_keys=True)
        exporter.write(tree, f)

    print(f'node count: {len(tree.descendants)}')


if __name__ == "__main__":
    main()
