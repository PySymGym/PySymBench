import json
from collections import defaultdict


class Methods:
    def __init__(self, data_filepath, output_filepath):
        with open(data_filepath, "r") as f:
            data = json.load(f)

        self.methods = defaultdict(list)
        groups = defaultdict(list)
        for item in data:
            groups[item["AssemblyFullName"]].append(item)
            self.methods[item["AssemblyFullName"]] = []

        tree = []
        for assembly, items in groups.items():
            node = {
                "title": assembly[:-4],
                "value": assembly,
                "children": []
            }
            seen_children = set()
            for child in items:
                name = child["NameOfObjectToCover"]
                if name in seen_children:
                    continue
                seen_children.add(name)
                dll_method = f"{assembly},{name}"
                self.methods[assembly].append(dll_method)
                child_node = {
                    "title": name,
                    "value": dll_method
                }
                node["children"].append(child_node)
            tree.append(node)

        with open(output_filepath, "w") as f:
            f.write("export const METHODS = ")
            json.dump(tree, f, indent=4)

    def get_methods_list(self, selection_list):
        selected_methods = []
        for item in selection_list:
            if item in self.methods.keys():
                selected_methods.extend(self.methods[item])
            else:
                selected_methods.append(item)
        return selected_methods
