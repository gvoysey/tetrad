import anytree
from tetrad.bio import gain
from tetrad.tree_io import read_tree
from tetrad.base import data_path
from tetrad.make_tree import make_tetrad
import sys
import csv
import os


def main(treepath):
    gains = {}
    tree = read_tree(treepath)
    leaves = anytree.findall(tree, filter_=lambda x: x.is_leaf)
    for leaf in leaves:
        tetrad = leaf.path[1:]  # omit root
        gains[tetrad] = gain(tetrad)

    with open('results.csv', 'w') as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(['tetrad label', 'gain function score'])
        for label, gain_score in gains.items():
            tetrad_labels = []
            for x in label:
                tetrad_labels.extend(x.name)
            tetrad_name = ','.join(tetrad_labels)
            writer.writerow([tetrad_name, gain_score])
    print(f"wrote {os.path.abspath('results.csv')}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.path.join(data_path, 'full_tree.json'))
