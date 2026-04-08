import json
from collections import defaultdict

FRONT_SELECTION_PREFIX = "export const METHODS = "


class Methods:
    @staticmethod
    def save_selection_to_frontend_file(
            selection_dataset, front_selection_resource_path
    ):
        with open(front_selection_resource_path, "w") as f:
            f.write("export const METHODS = ")
            json.dump(selection_dataset, f, indent=4)

    @staticmethod
    def parse_frontend_file_to_dll_methods(
            front_selection_resource_path,
    ):
        with open(front_selection_resource_path, "r") as f:
            content = f.read()
        json_str = content[len(FRONT_SELECTION_PREFIX):]
        selection_tree = json.loads(json_str)

        dll_methods = defaultdict(list)
        for node in selection_tree:
            dll_name = node["title"] + ".dll"
            for child in node["children"]:
                dll_methods[dll_name].append(child["value"])
        return dll_methods

    @staticmethod
    def build_selection_tree_from_dataset(data_filepath):
        with open(data_filepath, "r") as f:
            data = json.load(f)

        groups = defaultdict(list)
        for item in data:
            groups[item["AssemblyFullName"]].append(item)

        dataset_tree = []
        for assembly, items in groups.items():
            node = {"title": assembly[:-4], "value": assembly, "children": []}
            seen_children = set()
            for child in items:
                name = child["NameOfObjectToCover"]
                if name in seen_children:
                    continue
                seen_children.add(name)
                dll_and_method = f"{assembly},{name}"
                child_node = {"title": name, "value": dll_and_method}
                node["children"].append(child_node)
            dataset_tree.append(node)
        return dataset_tree

    @staticmethod
    def expand_selected_items_to_methods(dll_methods: defaultdict, selected):
        launch_info_methods = []
        for item in selected:
            if item in dll_methods.keys():
                launch_info_methods.extend(dll_methods[item])
            else:
                launch_info_methods.append(item)
        return launch_info_methods
