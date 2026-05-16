from unittest.mock import MagicMock

import pytest

from backend.file_utils.runstrat_metrics import RunstratMetrics
from backend.utils import task as task_module

TASK_UID = "abc123"
FAKE_METRICS = RunstratMetrics(
    total_tests=10,
    total_errors=1,
    mean_coverage=0.75,
    median_coverage=0.80,
    total_time_sec=42.0,
    methods_with_results=3,
)


@pytest.fixture
def mock_task_deps(monkeypatch):
    mocks = {
        "run_pipeline": MagicMock(),
        "upload_file": MagicMock(side_effect=lambda src, key: key),
        "save_experiment": MagicMock(return_value=1),
        "compute_metrics": MagicMock(return_value=FAKE_METRICS),
        "combine_metrics": MagicMock(return_value=FAKE_METRICS),
        "merge_csvs": MagicMock(),
        "send_results_email": MagicMock(),
        "send_failed_email": MagicMock(),
        "reset_dirs": MagicMock(),
        "mark_completed": MagicMock(),
        "count_methods": MagicMock(return_value=5),
        "copy2": MagicMock(),
        "makedirs": MagicMock(),
    }

    monkeypatch.setattr(task_module, "run_pipeline", mocks["run_pipeline"])
    monkeypatch.setattr(task_module, "upload_file", mocks["upload_file"])
    monkeypatch.setattr(task_module, "save_experiment", mocks["save_experiment"])
    monkeypatch.setattr(task_module, "compute_metrics", mocks["compute_metrics"])
    monkeypatch.setattr(task_module, "combine_metrics", mocks["combine_metrics"])
    monkeypatch.setattr(task_module, "merge_csvs", mocks["merge_csvs"])
    monkeypatch.setattr(
        task_module, "send_experiment_results_by_email", mocks["send_results_email"]
    )
    monkeypatch.setattr(
        task_module, "send_task_failed_email", mocks["send_failed_email"]
    )
    monkeypatch.setattr(task_module, "reset_dirs", mocks["reset_dirs"])
    monkeypatch.setattr(task_module, "mark_task_completed", mocks["mark_completed"])
    monkeypatch.setattr(task_module, "_count_methods_in_csv", mocks["count_methods"])
    monkeypatch.setattr(task_module.shutil, "copy2", mocks["copy2"])
    monkeypatch.setattr(task_module.os, "makedirs", mocks["makedirs"])

    monkeypatch.setattr(
        task_module,
        "get_tmp_thread_files",
        lambda uid: [f"/tmp/{uid}/uploads", f"/tmp/{uid}/results"],
    )
    return mocks


def _run_task(language: str = "csharp") -> None:
    task_module.process_and_cleanup_task.run(
        TASK_UID, "user@example.com", "exp", "model.onnx", language
    )


def test_success_uploads_model_and_results_to_minio(mock_task_deps):
    _run_task(language="csharp")

    object_keys = [
        call.args[1] for call in mock_task_deps["upload_file"].call_args_list
    ]
    assert f"models/{TASK_UID}/model.onnx" in object_keys
    assert f"results/{TASK_UID}/csharp/AI.csv" in object_keys


def test_success_saves_experiment_to_db(mock_task_deps):
    _run_task(language="csharp")

    mock_task_deps["save_experiment"].assert_called_once()
    kwargs = mock_task_deps["save_experiment"].call_args.kwargs
    assert kwargs["experiment_name"] == "exp"
    assert kwargs["model_name"] == "model"
    assert kwargs["email"] == "user@example.com"
    assert kwargs["language"] == "csharp"
    assert kwargs["metrics"] is FAKE_METRICS


def test_success_sends_results_email(mock_task_deps):
    _run_task(language="csharp")

    mock_task_deps["send_results_email"].assert_called_once()
    args, kwargs = mock_task_deps["send_results_email"].call_args
    assert args[0] == "user@example.com"
    assert "csharp" in args[1]
    assert args[2] == "exp"
    assert args[3] == "model.onnx"


def test_success_does_not_send_failure_email(mock_task_deps):
    _run_task(language="csharp")
    mock_task_deps["send_failed_email"].assert_not_called()


def test_pipeline_failure_sends_failure_email_instead_of_results(mock_task_deps):
    mock_task_deps["run_pipeline"].side_effect = RuntimeError("docker died")

    _run_task(language="csharp")

    mock_task_deps["send_results_email"].assert_not_called()
    mock_task_deps["send_failed_email"].assert_called_once_with(
        "user@example.com", "exp", "model.onnx"
    )


def test_upload_failure_sends_failure_email(mock_task_deps):
    mock_task_deps["upload_file"].side_effect = RuntimeError("minio down")

    _run_task(language="csharp")

    mock_task_deps["send_failed_email"].assert_called_once()
    mock_task_deps["send_results_email"].assert_not_called()


def test_db_failure_sends_failure_email(mock_task_deps):
    mock_task_deps["save_experiment"].side_effect = RuntimeError("db down")

    _run_task(language="csharp")

    mock_task_deps["send_failed_email"].assert_called_once()
    mock_task_deps["send_results_email"].assert_not_called()


def test_cleanup_runs_in_finally_on_success(mock_task_deps):
    _run_task(language="csharp")

    mock_task_deps["reset_dirs"].assert_called_once_with(
        [f"/tmp/{TASK_UID}/uploads", f"/tmp/{TASK_UID}/results"]
    )
    mock_task_deps["mark_completed"].assert_called_once_with(TASK_UID)


def test_cleanup_runs_in_finally_on_pipeline_failure(mock_task_deps):
    mock_task_deps["run_pipeline"].side_effect = RuntimeError("docker died")

    _run_task(language="csharp")

    mock_task_deps["reset_dirs"].assert_called_once()
    mock_task_deps["mark_completed"].assert_called_once_with(TASK_UID)


def test_language_all_runs_pipeline_per_language(mock_task_deps):
    _run_task(language="all")

    assert mock_task_deps["run_pipeline"].call_count == 3


def test_language_all_saves_aggregated_experiment(mock_task_deps):
    _run_task(language="all")

    assert mock_task_deps["save_experiment"].call_count == 4
    languages_saved = [
        call.kwargs["language"]
        for call in mock_task_deps["save_experiment"].call_args_list
    ]
    assert languages_saved == ["csharp", "java", "cpp", "all"]
    mock_task_deps["merge_csvs"].assert_called_once()
    mock_task_deps["combine_metrics"].assert_called_once()


def test_failure_in_results_email_still_runs_cleanup(mock_task_deps):
    mock_task_deps["send_results_email"].side_effect = RuntimeError("smtp died")

    _run_task(language="csharp")

    mock_task_deps["send_failed_email"].assert_called_once()
    mock_task_deps["reset_dirs"].assert_called_once()
    mock_task_deps["mark_completed"].assert_called_once_with(TASK_UID)


def test_model_name_strips_onnx_extension(mock_task_deps):
    _run_task(language="csharp")

    kwargs = mock_task_deps["save_experiment"].call_args.kwargs
    assert kwargs["model_name"] == "model"
