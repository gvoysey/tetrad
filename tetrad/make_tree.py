import json
from itertools import combinations

import numpy as np
import sympy
from anytree import Node

gene_data = 'bloodspot_figure_2.json'

with open(gene_data, 'r') as f:
    antigens = json.load(f)
    antigens.pop('date_accessed')

dyads = list(combinations(antigens, 2))

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
    A = np.zeros((4, 4))
    # the (i,j)th element of A is 1 if the ith tetrad pair 
    # contains the jth unique string
    for i, pair in enumerate(tetrad):
        for j, e in enumerate(elements):
            if e in pair:
                A[i, j] = 1
    return sympy.Matrix(A).rref() == valid_scoring


def cost(pair):
    return 1
    A, B = pair
    A = list(antigens[A].values()).remove("MERGED_AML")
    B = list(antigens[B].values()).remove("MERGED_AML")
    cost = []
    for i, a, b in enumerate(zip(A, B)):
        cost.append((a ** 2 + b ** 2) * weights[i])
    return np.mean(cost)


def add_children(node: Node):
    if node.root.height > 5:
        return
    ancestor_dyads = [x.name for x in node.ancestors]


def main():
    # for x in combinations(dyads, 4):
    #     if is_valid(x):
    #         print(x)

    # generate an iterable of pairs.
    root = Node({})
    root.cost = -np.inf
    for bush_root in dyads:
        # BR is A and C
        br = Node(bush_root, parent=root)
        br.cost = cost(br.name)

        #all children are A and D
        children = [d for d in dyads if d != bush_root and d[0] == bush_root[0]]
        for child in children:
            # all grandchildren are B and C
            grandchildren = [d for d in dyads if d != bush_root and d!= child
                             and not any(d[0] in c for c in child)
                             and not any(d[1] in c for c in child)]

            for grandchild in grandchildren:
                # all greatgrandchildren are B and D
                greatgrandchildren =[d for d in dyads if d !=bush_root and d!= child and d !=grandchild
                                     and d[0]==grandchild[0]
                                     and d[1]==child[1]]
                for greatchild in grandchildren:
                    tetrad = [frozenset(bush_root),frozenset(child),frozenset(grandchild), frozenset(greatchild)]
                    if(is_valid(tetrad)):
                        print(tetrad)
                    else:
                        print('.', end='')





        print('erk.')
        # for pc in dyads:
        #     if pc != br.name:  # and len(pc.intersection(root.name)==1):
        #         x = Node(pc, parent=br)
        #         x.cost = cost(x.name)

                # for br in dyads:
                #     #br is "A and C"
                #     #children can be any of "A and D", "B and C", "B and D".
                #     # these are potential A and D and B and Cs.
                #     children = [c for c in dyads if len(c.intersection(test))==1]


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
