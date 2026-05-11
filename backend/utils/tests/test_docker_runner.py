from pathlib import Path
from unittest.mock import patch

import pytest

from backend.config.paths import (
    ARTIFACTS_AI2_CSV_FILE,
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    BASE_DIR,
)
from backend.utils import docker_runner
from backend.utils.docker_runner import (
    Compstrat,
    RunstratAI,
    RunstratAI2,
    RunstratBaseline,
    run_model_vs_model_pipeline,
    run_pipeline,
    run_publish_pipeline,
)

TEST_RESOURCES_DIR = BASE_DIR + "/utils/tests/resources/"
TEST_ARTIFACTS_BASELINE_CSV_FILE = (
    TEST_RESOURCES_DIR + "ExecutionTreeContributedCoverage.csv"
)
TEST_ARTIFACTS_AI_CSV_FILE = TEST_RESOURCES_DIR + "AI.csv"
TEST_ARTIFACTS_AI2_CSV_FILE = TEST_RESOURCES_DIR + "AI.csv"


@pytest.fixture
def test_env(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    def mock_get_thread_filepath(uid, filepath):
        if "uploads" in filepath:
            return filepath.replace("tmp/uploads", "utils/tests/resources")
        if filepath == ARTIFACTS_AI_CSV_FILE:
            return TEST_ARTIFACTS_AI_CSV_FILE
        if filepath == ARTIFACTS_AI2_CSV_FILE:
            return TEST_ARTIFACTS_AI2_CSV_FILE
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


def test_runstrat_ai2(test_env):
    uid = "test"
    RunstratAI2().run(uid)


def test_compstrat(test_env):
    uid = "test"
    Compstrat("BASELINE", ARTIFACTS_BASELINE_CSV_FILE, "AI", ARTIFACTS_AI_CSV_FILE).run(
        uid
    )


def test_compstrat_model_vs_model(test_env):
    uid = "test"
    Compstrat("MODEL1", ARTIFACTS_AI_CSV_FILE, "MODEL2", ARTIFACTS_AI2_CSV_FILE).run(
        uid
    )


def test_run_pipeline_calls_all_runners_in_order():
    uid = "test"
    call_order = []

    with (
        patch.object(
            RunstratBaseline, "run", side_effect=lambda u: call_order.append("baseline")
        ),
        patch.object(RunstratAI, "run", side_effect=lambda u: call_order.append("ai")),
        patch.object(
            Compstrat, "run", side_effect=lambda u: call_order.append("compstrat")
        ),
    ):
        run_pipeline(uid)

    assert call_order == ["baseline", "ai", "compstrat"]


def test_run_model_vs_model_pipeline_calls_in_order():
    uid = "test"
    call_order = []

    with (
        patch.object(RunstratAI, "run", side_effect=lambda u: call_order.append("ai")),
        patch.object(
            RunstratAI2, "run", side_effect=lambda u: call_order.append("ai2")
        ),
        patch.object(
            Compstrat, "run", side_effect=lambda u: call_order.append("compstrat")
        ),
        patch.object(RunstratBaseline, "run") as mock_baseline,
    ):
        run_model_vs_model_pipeline(uid)

    assert call_order == ["ai", "ai2", "compstrat"]
    mock_baseline.assert_not_called()


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
