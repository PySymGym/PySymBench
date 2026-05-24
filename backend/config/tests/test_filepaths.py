import pytest

from backend.config.paths import (
    RESULTS_DIR,
    TMP_FILE_DIR,
    UPLOAD_DIR,
    get_thread_filepath,
    get_tmp_thread_files,
)


@pytest.mark.parametrize(
    "uid, filepath, expected",
    [
        ("", RESULTS_DIR, RESULTS_DIR),
        ("123", UPLOAD_DIR, TMP_FILE_DIR + "/123uploads"),
    ],
)
def test_get_thread_filepath(uid, filepath, expected):
    assert get_thread_filepath(uid, filepath) == expected


@pytest.mark.parametrize(
    "uid, expected",
    [
        ("", [UPLOAD_DIR, RESULTS_DIR]),
        ("123", [TMP_FILE_DIR + "/123uploads", TMP_FILE_DIR + "/123results"]),
    ],
)
def test_get_created_tmp_files(uid, expected):
    assert get_tmp_thread_files(uid) == expected
