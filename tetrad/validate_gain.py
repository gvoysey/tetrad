import os
import sys

from tetrad.base import data_path
from tetrad.tree_io import read_tree, extract_tetrads_to_csv


def main(treepath):
    tree = read_tree(treepath)
    extract_tetrads_to_csv(tree, 'full_tree_tetrads.csv')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.path.join(data_path, 'full_tree.json'))
