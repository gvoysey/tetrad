from anytree.importer import JsonImporter


def read_tree(file_path):
    """Deserialize a tree from a saved JSON file"""
    importer = JsonImporter()
    with open(file_path, 'r') as j:
        json_tree = j.read().replace("_name", "name")
    root = importer.import_(json_tree)
    root.cost = None
    return root

