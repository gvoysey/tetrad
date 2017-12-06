import anytree
from tetrad.bio import gain
from tetrad.tree_io import read_tree
from tetrad.base import data_path
from tetrad.branch_and_bound import cumulative_cost
import sys
import os
import pandas as pd


def make_tetrad_str(tetrad):
    tetrad_labels = []
    for x in tetrad:
        tetrad_labels.extend(x.name)
    return ','.join(tetrad_labels)


def main(treepath):
    tetrads = {}
    tree = read_tree(treepath)
    leaves = anytree.findall(tree, filter_=lambda x: x.is_leaf)
    for leaf in leaves:
        tetrad = leaf.path[1:]  # omit root
        tetrads[tetrad] = (gain(tetrad), cumulative_cost(leaf))

    df = pd.DataFrame({make_tetrad_str(k): v for k, v in tetrads.items()}).transpose()
    df.columns = ['gain', 'cumulative_cost']
    df = df.sort_values('cumulative_cost')
    df.to_csv('results.csv')
    print(f"wrote {os.path.abspath('results.csv')}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.path.join(data_path, 'full_tree.json'))
