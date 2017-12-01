import json
from itertools import permutations
from collections import defaultdict

import numpy as np
import sympy
from anytree import Node

gene_data = 'bloodspot_figure_2.json'

with open(gene_data, 'r') as f:
    antigens = json.load(f)
    antigens.pop('date_accessed')

dyads = list(permutations(antigens, 2))

weights = np.ones(41)

valid_scoring = sympy.Matrix(np.array([[1, 0, 1, 0], [1, 0, 0, 1]
                                          , [0, 1, 1, 0], [0, 1, 0, 1]])
                             ).rref()


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


def cost(pair):
    return 1
    A, B = pair
    A = list(antigens[A].values()).remove("MERGED_AML")
    B = list(antigens[B].values()).remove("MERGED_AML")
    cost = []
    for i, a, b in enumerate(zip(A, B)):
        cost.append((a ** 2 + b ** 2) * weights[i])
    return np.mean(cost)


def main():
    root = Node({})
    root.cost = -np.inf
    # (a, c), (a, d), (b, c), (b, d)
    bushes = defaultdict(list)
    for bush_root in dyads:
        # bush_root is A and C
        br = Node(bush_root, parent=root)
        br.cost = cost(br.name)

        # all children are A and D
        children = [d for d in dyads if bush_root[0] == d[0] and bush_root[1] != d[1]]
        for child in children:
            # all grandchildren are B and C
            grandchildren = [d for d in dyads if
                             d[0] != bush_root[0]  # not a
                             and d[0] != child[1]  # not d
                             and d[1] == bush_root[1]  # is c
                             ]

            for grandchild in grandchildren:
                # all greatgrandchildren are B and D
                greatgrandchildren = [d for d in dyads if d[0] == grandchild[0]
                                      and d[1] == child[1]]
                for greatchild in greatgrandchildren:
                    tetrad = [frozenset(bush_root), frozenset(child), frozenset(grandchild), frozenset(greatchild)]
                    if is_valid(tetrad):
                        r = Node(bush_root)
                        c = Node(child, parent=r)
                        gc = Node(grandchild, parent=c)
                        ggc = Node(greatchild, parent=gc)
                        bushes[r] = c
                        print(tetrad)
        print('buhh')


if __name__ == "__main__":
    main()


# from anytree import node
# from anytree import Node
# foo = Node('foo')
# bar = Node('bar',parent=foo)
# bar.ancestors
# (x.name for x in bar.ancestors)
# list(x.name for x in bar.ancestors)
# foo.height
# bar.height
# bar.root
# bar.root.height
# list(x.name for x in bar.ancestors).append(bar.name)
# print(list(x.name for x in bar.ancestors).append(bar.name))
# print([x.name for x in bar.ancestors].append(bar.name))
# valid_tetrad= [{'a','c'},{'a','d'},{'b','c'},{'b','d'}]
# invalid_tetrad= [{'a','a'},{'a','d'},{'b','c'},{'b','d'}]
# {'a','c'} ^ {'a','d'}
# from collections import Counter
# Counter(*valid_tetrad)
# Counter(valid_tetrad)
# valid_tetrad
# valid_tetrad = [frozenset(x) for x in valid_tetrad]
# Counter(valid_tetrad)
# from itertools import chain
# counter(chain(valid_tetrad))
# Counter(chain(valid_tetrad))
# Counter(chain(*valid_tetrad))
# all(Counter(chain(*valid_tetrad)).values() ==2)
# Counter(chain(*valid_tetrad)).values()
# all(x == 2 for x in Counter(chain(*valid_tetrad)).values())
# all(x == 2 for x in Counter(chain(*valid_tetrad))
# )
# all(x == 2 for x in Counter(chain(*valid_tetrad)).values())
# history
