"""Prune a tree of tetrads."""
import numpy as np
import anytree
from anytree.importer import JsonImporter
from anytree import Node
import json
import sys


def main():
    importer = JsonImporter()
    with open(sys.argv[1], 'r') as j:
        json_tree = j.read().replace("_name", "name")
    tree = importer.import_(json_tree)

    print('tree')


if __name__ == "__main__":
    sys.exit(main())
