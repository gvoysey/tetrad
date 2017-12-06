from anytree.importer import JsonImporter
import anytree
import pandas as pd
import os
from tetrad.branch_and_bound import cumulative_cost
from tetrad.bio import gain


def make_tetrad_str(tetrad):
    tetrad_labels = []
    for x in tetrad:
        tetrad_labels.extend(x.name)
    return ','.join(tetrad_labels)


def read_tree(file_path):
    """Deserialize a tree from a saved JSON file"""
    importer = JsonImporter()
    with open(file_path, 'r') as j:
        json_tree = j.read().replace("_name", "name")
    root = importer.import_(json_tree)
    root.cost = None
    return root


def extract_tetrads_to_csv(tree, outfile):
    tetrads = {}
    leaves = anytree.findall(tree, filter_=lambda x: x.is_leaf)
    for leaf in leaves:
        tetrad = leaf.path[1:]  # omit root
        tetrads[tetrad] = (gain(tetrad), cumulative_cost(leaf))

    df = pd.DataFrame({make_tetrad_str(k): v for k, v in tetrads.items()}).transpose()
    df.columns = ['gain', 'cumulative_cost']
    df = df.sort_values('cumulative_cost')
    df.to_csv(outfile)
    print(f"wrote {os.path.abspath(outfile)}")
