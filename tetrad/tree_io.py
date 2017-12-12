from anytree.importer import JsonImporter
import anytree
from anytree import Node
import pandas as pd
import os

from tetrad.bio import gain


def cumulative_cost(node: Node):
    prev_cost = sum(x.cost for x in node.ancestors if not x.is_root)
    if not node.is_root:
        return prev_cost + node.cost
    else:
        return None


def make_tetrad_str(tetrad):
    tetrad_labels = []
    for x in tetrad:
        tetrad_labels.extend(x.name)
    return ','.join(tetrad_labels)


def read_tree(file_path: str):
    """Deserialize a tree from a saved JSON file"""
    importer = JsonImporter()
    with open(file_path, 'r') as j:
        json_tree = j.read().replace("_name", "name")
    root = importer.import_(json_tree)
    root.cost = None
    return root


def extract_tetrads_to_csv(tree: Node, outfile: str):
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


def read_tetrad_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['ratio'] = df['gain'] / df['cost']
    df = df.transpose().dropna(axis=1, how='all').transpose()
    df = df.sort_values('ratio', ascending=False)
    df[['cost', 'gain', 'ratio']] = df[['cost', 'gain', 'ratio']].apply(pd.to_numeric)
    return df
