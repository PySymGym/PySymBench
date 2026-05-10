from pathlib import Path
from unittest.mock import patch

import pytest

from backend.config.paths import (
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    BASE_DIR,
)
from backend.utils import docker_runner
from backend.utils.docker_runner import (
    Compstrat,
    RunstratAI,
    RunstratBaseline,
    run_publish_pipeline,
)

TEST_RESOURCES_DIR = BASE_DIR + "/utils/tests/resources/"
TEST_ARTIFACTS_BASELINE_CSV_FILE = (
    TEST_RESOURCES_DIR + "ExecutionTreeContributedCoverage.csv"
)
TEST_ARTIFACTS_AI_CSV_FILE = TEST_RESOURCES_DIR + "AI.csv"


@pytest.fixture
def test_env(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    def mock_get_thread_filepath(uid, filepath):
        if "uploads" in filepath:
            return filepath.replace("tmp/uploads", "utils/tests/resources")
        if filepath == ARTIFACTS_AI_CSV_FILE:
            return TEST_ARTIFACTS_AI_CSV_FILE
        if filepath == ARTIFACTS_BASELINE_CSV_FILE:
            return TEST_ARTIFACTS_BASELINE_CSV_FILE

        if "results" in filepath:
            return str(results_dir / Path(filepath).name)

        return filepath.replace("tmp", "utils/tests/resources")

    monkeypatch.setattr(docker_runner, "get_thread_filepath", mock_get_thread_filepath)

    return {
        "results_dir": results_dir,
    }


def test_runstrat_baseline(test_env):
    uid = "test"
    RunstratBaseline().run(uid)


def test_runstrat_ai(test_env):
    uid = "test"
    RunstratAI().run(uid)


def test_compstrat(test_env):
    uid = "test"
    Compstrat().run(uid)


def test_run_publish_pipeline_calls_only_runstrat_ai():
    uid = "test"
    with (
        patch.object(RunstratAI, "run") as mock_ai,
        patch.object(RunstratBaseline, "run") as mock_baseline,
        patch.object(Compstrat, "run") as mock_compstrat,
    ):
        run_publish_pipeline(uid)

    mock_ai.assert_called_once_with(uid)
    mock_baseline.assert_not_called()
    mock_compstrat.assert_not_called()
