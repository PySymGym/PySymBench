import csv
import os
from io import BytesIO
from unittest.mock import Mock

import pytest
from fastapi import UploadFile

from backend.config.paths import TMP_FILE_DIR
from backend.file_utils.csv_methods_writer import write_launch_info_to_csv
from backend.file_utils.files import reset_dirs, save_upload_file


@pytest.mark.parametrize(
    "filepaths",
    [
        ([TMP_FILE_DIR + "/test"]),
        ([TMP_FILE_DIR + "/test1", TMP_FILE_DIR + "/test2"]),
    ],
)
def test_removing_tmp_files(filepaths):
    for path in filepaths:
        os.makedirs(path)
    reset_dirs(filepaths)
    for path in filepaths:
        assert not os.path.exists(path)


def test_save_upload_file(tmp_path):
    test_content = b"Hello, World!" * 1000
    dest_path = tmp_path / "test.txt"

    mock_file = BytesIO(test_content)
    upload_file = Mock(spec=UploadFile)
    upload_file.file = mock_file

    save_upload_file(upload_file, str(dest_path))

    assert dest_path.exists()
    with open(dest_path, "rb") as f:
        saved_content = f.read()

    assert saved_content == test_content


def test_write_launch_info_to_csv(tmp_path):
    output_file = tmp_path / "launch_info.csv"

    parsed_methods = [
        "ManuallyCollected.dll,BinSearchMain",
        "ManuallyCollected.dll,BellmanFord",
        "ManuallyCollected.dll,BinaryMaze1BFS",
    ]

    write_launch_info_to_csv(
        parsed_methods=parsed_methods, output_file=str(output_file)
    )

    assert output_file.exists()

    with open(output_file) as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["dll", "method"]

    expected_data = [
        ["ManuallyCollected.dll", "BinSearchMain"],
        ["ManuallyCollected.dll", "BellmanFord"],
        ["ManuallyCollected.dll", "BinaryMaze1BFS"],
    ]

    assert rows[1:] == expected_data
