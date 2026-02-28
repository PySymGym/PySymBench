import shutil

import pytest, os, csv

from backend.config.paths import TMP_FILE_DIR
from backend.file_utils.csv_methods_writer import write_launch_info_to_csv
from backend.file_utils.files import reset_dirs, save_upload_file
from unittest.mock import Mock
from fastapi import UploadFile
from io import BytesIO


@pytest.mark.parametrize(
    "filepaths",
    [
        ([TMP_FILE_DIR + "/test0"]),
        ([TMP_FILE_DIR + "/test1", TMP_FILE_DIR + "/test2"]),
    ],
)
def test_removing_tmp_files(filepaths):
    for path in filepaths:
        os.makedirs(path)
    reset_dirs(filepaths)
    for path in filepaths:
        assert not os.path.exists(path)


def test_save_upload_file():
    test_content = b"Hello, World!" * 1000
    upload_dir = TMP_FILE_DIR + "/test_save_upload/"
    dest_path = upload_dir + "test.txt"

    mock_file = BytesIO(test_content)
    upload_file = Mock(spec=UploadFile)
    upload_file.file = mock_file

    save_upload_file(upload_file, dest_path)

    assert os.path.exists(dest_path)
    with open(dest_path, "rb") as f:
        saved_content = f.read()
    shutil.rmtree(upload_dir)
    assert saved_content == test_content


def test_write_launch_info_to_csv():
    upload_dir = TMP_FILE_DIR + "/test_write_launch_info_to_csv/"
    os.makedirs(upload_dir)
    output_file = upload_dir + "launch_info.csv"
    parsed_methods = [
        "ManuallyCollected.dll,BinSearchMain",
        "ManuallyCollected.dll,BellmanFord",
        "ManuallyCollected.dll,BinaryMaze1BFS",
    ]

    write_launch_info_to_csv(parsed_methods=parsed_methods, output_file=output_file)

    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["dll", "method"]

    expected_data = [
        ["ManuallyCollected.dll", "BinSearchMain"],
        ["ManuallyCollected.dll", "BellmanFord"],
        ["ManuallyCollected.dll", "BinaryMaze1BFS"],
    ]
    shutil.rmtree(upload_dir)
    assert rows[1:] == expected_data
