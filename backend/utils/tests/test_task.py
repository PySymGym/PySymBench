from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.file_utils.runstrat_metrics import RunstratMetrics
from backend.main import app
from backend.utils import task as task_module

client = TestClient(app)

TASK_UID = "abc123"
FAKE_METRICS = RunstratMetrics(
    total_tests=10,
    total_errors=1,
    mean_coverage=0.75,
    median_coverage=0.80,
    total_time_sec=42.0,
)


@pytest.fixture
def mock_task_deps(monkeypatch):
    mock_run = MagicMock()
    mock_send = MagicMock()
    mock_reset = MagicMock()
    mock_get_files = MagicMock(return_value=["/tmp/fake/uploads", "/tmp/fake/results"])

    monkeypatch.setattr(task_module, "run_pipeline", mock_run)
    monkeypatch.setattr(task_module, "reset_dirs", mock_reset)
    monkeypatch.setattr(task_module, "get_tmp_thread_files", mock_get_files)

    return {
        "run_pipeline": mock_run,
        "send_email": mock_send,
        "reset_dirs": mock_reset,
        "get_tmp_thread_files": mock_get_files,
    }


def test_task_cleanup_runs_on_success(mock_task_deps):
    task_module.process_and_cleanup_task.run(TASK_UID, "a@b.com", "exp", "model.onnx")
    mock_task_deps["reset_dirs"].assert_called_once()


def test_task_cleanup_runs_on_pipeline_failure(mock_task_deps):
    mock_task_deps["run_pipeline"].side_effect = RuntimeError("docker died")
    task_module.process_and_cleanup_task.run(TASK_UID, "a@b.com", "exp", "model.onnx")
    mock_task_deps["reset_dirs"].assert_called_once()


def test_task_no_email_on_pipeline_failure(mock_task_deps):
    mock_task_deps["run_pipeline"].side_effect = RuntimeError("docker died")
    task_module.process_and_cleanup_task.run(TASK_UID, "a@b.com", "exp", "model.onnx")
    mock_task_deps["send_email"].assert_not_called()


def test_task_sends_email_on_success(mock_task_deps):
    task_module.process_and_cleanup_task.run(TASK_UID, "a@b.com", "exp", "model.onnx")
    mock_task_deps["send_email"].assert_called_once()


def test_task_cleanup_receives_correct_uid(mock_task_deps):
    task_module.process_and_cleanup_task.run(TASK_UID, "a@b.com", "exp", "model.onnx")
    mock_task_deps["get_tmp_thread_files"].assert_called_once_with(TASK_UID)
