import os
import shutil

import pytest

from backend.config.paths import (
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    BASE_DIR,
)
from backend.utils import docker_runner
from backend.utils.docker_runner import RunstratBaseline, RunstratAI, Compstrat

TEST_RESOURCES_DIR = BASE_DIR + "/utils/tests/resources/"
TEST_ARTIFACTS_BASELINE_CSV_FILE = (
    TEST_RESOURCES_DIR + "ExecutionTreeContributedCoverage.csv"
)
TEST_ARTIFACTS_AI_CSV_FILE = TEST_RESOURCES_DIR + "AI.csv"
TEST_RESULTS_DIR = BASE_DIR + "/utils/tests/resources/results"


@pytest.fixture(autouse=True)
def auto_test_results_dir():
    os.makedirs(TEST_RESULTS_DIR, exist_ok=True)
    yield
    shutil.rmtree(TEST_RESULTS_DIR)


@pytest.fixture
def mock_paths(monkeypatch):
    def mock_get_thread_filepath(uid, filepath):
        if "uploads" in filepath:
            return filepath.replace("tmp/uploads", "utils/tests/resources")
        if filepath == ARTIFACTS_AI_CSV_FILE:
            return TEST_ARTIFACTS_AI_CSV_FILE
        if filepath == ARTIFACTS_BASELINE_CSV_FILE:
            return TEST_ARTIFACTS_BASELINE_CSV_FILE
        return filepath.replace("tmp", "utils/tests/resources")

    monkeypatch.setattr(docker_runner, "get_thread_filepath", mock_get_thread_filepath)


def test_runstrat_baseline(mock_paths):
    uid = "test"
    RunstratBaseline().run(uid)


def test_runstrat_ai(mock_paths):
    uid = "test"
    RunstratAI().run(uid)


def test_compstrat(mock_paths):
    uid = "test"
    Compstrat().run(uid)
