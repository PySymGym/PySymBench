import json
from collections import defaultdict
from tempfile import NamedTemporaryFile

from backend.utils.methods_handler import Methods


def test_write_selection_dataset_to_front_file():
    test_data = [
        {"title": "Assembly1", "value": "Assembly1.dll", "children": []},
        {"title": "Assembly2", "value": "Assembly2.dll", "children": []},
    ]

    with NamedTemporaryFile(mode="w+", suffix=".js") as temp_file:
        Methods.save_selection_to_frontend_file(test_data, temp_file.name)

        temp_file.seek(0)
        content = temp_file.read()

        assert content.startswith("export const METHODS = ")
        json_str = content[len("export const METHODS = "):]
        written_data = json.loads(json_str)
        assert written_data == test_data


def test_write_selection_dataset_to_front_file_empty():
    with NamedTemporaryFile(mode="w+", suffix=".js") as temp_file:
        Methods.save_selection_to_frontend_file([], temp_file.name)

        temp_file.seek(0)
        content = temp_file.read()
        json_str = content[len("export const METHODS = "):]
        assert json.loads(json_str) == []


def test_get_dlls_with_all_methods_dict_from_front_options_file():
    test_data = [
        {
            "title": "Assembly1",
            "value": "Assembly1.dll",
            "children": [
                {"title": "Method1", "value": "Assembly1.dll,Method1"},
                {"title": "Method2", "value": "Assembly1.dll,Method2"},
            ],
        },
        {
            "title": "Assembly2",
            "value": "Assembly2.dll",
            "children": [{"title": "Method3", "value": "Assembly2.dll,Method3"}],
        },
    ]

    with NamedTemporaryFile(mode="w+", suffix=".js") as temp_file:
        Methods.save_selection_to_frontend_file(test_data, temp_file.name)

        result = Methods.parse_frontend_file_to_dll_methods(temp_file.name)

        expected = defaultdict(
            list,
            {
                "Assembly1.dll": ["Assembly1.dll,Method1", "Assembly1.dll,Method2"],
                "Assembly2.dll": ["Assembly2.dll,Method3"],
            },
        )

        assert dict(result) == dict(expected)


def test_get_dlls_with_all_methods_dict_empty_file():
    with NamedTemporaryFile(mode="w+", suffix=".js") as temp_file:
        Methods.save_selection_to_frontend_file([], temp_file.name)

        result = Methods.parse_frontend_file_to_dll_methods(temp_file.name)

        assert dict(result) == {}


def test_parse_dataset_file_for_front_selection():
    test_data = [
        {"AssemblyFullName": "Assembly1.dll", "NameOfObjectToCover": "Method1"},
        {"AssemblyFullName": "Assembly1.dll", "NameOfObjectToCover": "Method2"},
        {"AssemblyFullName": "Assembly2.dll", "NameOfObjectToCover": "Method3"},
    ]

    with NamedTemporaryFile(mode="w+", suffix=".json") as temp_file:
        json.dump(test_data, temp_file)
        temp_file.flush()

        result = Methods.build_selection_tree_from_dataset(temp_file.name)

        assert len(result) == 2

        assembly1_node = next(node for node in result if node["title"] == "Assembly1")
        assert assembly1_node["value"] == "Assembly1.dll"
        assert len(assembly1_node["children"]) == 2
        assert assembly1_node["children"][0]["title"] == "Method1"
        assert assembly1_node["children"][0]["value"] == "Assembly1.dll,Method1"

        assembly2_node = next(node for node in result if node["title"] == "Assembly2")
        assert len(assembly2_node["children"]) == 1
        assert assembly2_node["children"][0]["value"] == "Assembly2.dll,Method3"


def test_parse_dataset_file_duplicate_methods():
    test_data = [
        {"AssemblyFullName": "Assembly1.dll", "NameOfObjectToCover": "Method1"},
        {"AssemblyFullName": "Assembly1.dll", "NameOfObjectToCover": "Method1"},
    ]

    with NamedTemporaryFile(mode="w+", suffix=".json") as temp_file:
        json.dump(test_data, temp_file)
        temp_file.flush()

        result = Methods.build_selection_tree_from_dataset(temp_file.name)

        assert len(result[0]["children"]) == 1


def test_get_launch_info_list_from_selected():
    dll_methods = defaultdict(
        list,
        {
            "Assembly1.dll": ["Assembly1.dll,Method1", "Assembly1.dll,Method2"],
            "Assembly2.dll": ["Assembly2.dll,Method3"],
        },
    )

    selected = ["Assembly1.dll", "Assembly2.dll,Method3", "Assembly2.dll,Method4"]

    result = Methods.expand_selected_items_to_methods(dll_methods, selected)

    expected = [
        "Assembly1.dll,Method1",
        "Assembly1.dll,Method2",
        "Assembly2.dll,Method3",
        "Assembly2.dll,Method4",
    ]
    assert result == expected


def test_get_launch_info_list_from_selected_no_dlls():
    dll_methods = defaultdict(list)
    selected = [
        "Assembly1.dll,Method1",
        "Assembly2.dll,Method2",
        "Assembly3.dll,Method3",
    ]

    result = Methods.expand_selected_items_to_methods(dll_methods, selected)

    assert result == selected


def test_get_launch_info_list_from_selected_empty():
    dll_methods = defaultdict(list, {"Assembly1.dll": ["Method1"]})

    result = Methods.expand_selected_items_to_methods(dll_methods, [])

    assert result == []


def test_integration_full_flow():
    original_data = [
        {"AssemblyFullName": "Test.dll", "NameOfObjectToCover": "Method1"},
        {"AssemblyFullName": "Test.dll", "NameOfObjectToCover": "Method2"},
    ]

    with (
        NamedTemporaryFile(mode="w+", suffix=".json") as data_file,
        NamedTemporaryFile(mode="w+", suffix=".js") as front_file,
    ):
        json.dump(original_data, data_file)
        data_file.flush()

        frontend_data = Methods.build_selection_tree_from_dataset(data_file.name)

        Methods.save_selection_to_frontend_file(frontend_data, front_file.name)

        dll_methods = Methods.parse_frontend_file_to_dll_methods(front_file.name)

        selected = ["Test.dll"]
        launch_info = Methods.expand_selected_items_to_methods(dll_methods, selected)

        assert len(launch_info) == 2
        assert "Test.dll,Method1" in launch_info
        assert "Test.dll,Method2" in launch_info
