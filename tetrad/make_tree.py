import json
from itertools import permutations, combinations

import numpy as np
import sympy
from anytree import Node
from anytree.exporter import DotExporter

from tetrad.cost import cost, SURFACE_TARGETS
from datetime import datetime
#gene_data = 'bloodspot_figure_2.json'
start = datetime.now()
# with open(gene_data, 'r') as f:
#     antigens = json.load(f)
#     antigens.pop('date_accessed')

dyad_pairs = list(combinations(SURFACE_TARGETS, 2))
dyads = list(permutations(SURFACE_TARGETS, 2))

valid_scoring = sympy.Matrix(np.array([[1, 0, 1, 0], [1, 0, 0, 1]
                                     , [0, 1, 1, 0], [0, 1, 0, 1]])
                             ).rref()
dyad_costs = {k: cost(k) for k in (frozenset(d) for d in dyad_pairs)}


def get_cost(dyad):
    return dyad_costs[frozenset(dyad)]


def is_valid(tetrad):
    """Check if a given input obeys the correct form 
    (a,c), (a,d), (b,c), (b,d)"""
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
    return sympy.Matrix(tetrad_state).rref() == valid_scoring


def make_tetrad(*args):
    """makes a frozenset tetrad from a list"""
    return frozenset([frozenset(x) for x in args])


def add_node(tetrad, parent_node):
    matches = [x for x in parent_node.children if x.name == tetrad]
    if not any(matches):
        n = Node(tetrad)
        n.cost = get_cost(tetrad)
        n.parent = parent_node
    else:
        n = matches[0]
    return n


def main():
    valid_tetrads = set()
    root = Node('root')
    root.cost = 0
    # (a, c), (a, d), (b, c), (b, d)
    # bush_root is A and C
    for parent in dyad_pairs:
        # all children are A and D
        br_children = [d for d in dyads if
                       parent[0] == d[0]  # is a
                       and parent[1] != d[1]]  # is possibly D
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
                    # tetrad = [frozenset(bush_root), frozenset(child), frozenset(grandchild), frozenset(greatchild)]
                    tetrad = make_tetrad(parent, child, grandchild, greatgrandchild)

                    if is_valid(tetrad):  # and tetrad not in valid_tetrads:
                        valid_tetrads.add(tetrad)

                        parent_node = add_node(parent, root)
                        child_node = add_node(child, parent_node)
                        grandchild_node = add_node(grandchild, child_node)
                        greatgrandchild_node = add_node(greatgrandchild, grandchild_node)
                        #
                        # if not any(x for x in root.children if x.name == parent):
                        #     br = Node(parent)
                        #     br.cost = cost(br)
                        #     br.parent = root
                        #     try:
                        #         dyad_costs[parent] = br.cost
                        #     except KeyError:
                        #         pass
                        #
                        # else:
                        #     br = next(x for x in root.children if x.name == parent)
                        #
                        # if not any(x for x in br.children if x.name == child):
                        #     c = Node(child)
                        #     c.cost = cost(child)
                        #     c.parent = br
                        # else:
                        #     c = next((x for x in br.children if x.name == child))
                        #
                        # if not any(x for x in c.children if x.name == grandchild):
                        #     gc = Node(grandchild)
                        #     gc.cost = cost(gc)
                        #     gc.parent = c
                        # else:
                        #     gc = next(x for x in c.children if x.name == grandchild)
                        #
                        # if not any(x for x in gc.children if x.name == greatgrandchild):
                        #     ggc = Node(greatgrandchild)
                        #     ggc.cost = cost(ggc)
                        #     ggc.parent = gc
                        # else:
                        #     ggc = next(x for x in gc.children if x.name == greatgrandchild)

        print(f'processed bush with root {parent}')
        if len(root.children) > 0:
            DotExporter(root).to_dotfile(f'test.dot')
    DotExporter(root).to_dotfile('full_tree.dot')
    print(f'took {(datetime.now() -start).total_seconds()} to generate full tree before pruning')


if __name__ == "__main__":
    main()
