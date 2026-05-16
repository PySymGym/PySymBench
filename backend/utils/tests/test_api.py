import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.utils import task as task_module

client = TestClient(app)

TASK_UID = "abc123"
COMPARISON_UID = "cmp456"


@pytest.fixture
def fake_uuid(monkeypatch):
    counter = {"i": 0}
    uids = [TASK_UID, COMPARISON_UID, "extra-uid-1", "extra-uid-2"]

    def _uuid():
        v = uids[min(counter["i"], len(uids) - 1)]
        counter["i"] += 1
        return v

    monkeypatch.setattr("backend.main.shortuuid.uuid", _uuid)
    return uids


@pytest.fixture
def upload_deps(fake_uuid):
    with (
        patch("backend.main.handle_upload") as mock_upload,
        patch("backend.main.process_and_cleanup_task") as mock_task,
        patch("backend.main.generate_cancel_token", return_value="tok-xyz"),
        patch("backend.main.send_task_started_email") as mock_email,
    ):
        yield {
            "upload": mock_upload,
            "task": mock_task,
            "email": mock_email,
        }


def test_upload_returns_task_uid(upload_deps):
    resp = client.post(
        "/api/upload",
        files={
            "file": ("model.onnx", io.BytesIO(b"fake-onnx"), "application/octet-stream")
        },
        data={"email": "user@example.com", "language": "csharp", "experiment": "exp"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["task_uid"] == TASK_UID
    assert body["experiment"] == "exp"
    assert body["filename"] == "model.onnx"
    assert body["email"] == "user@example.com"
    assert body["language"] == "csharp"


def test_upload_enqueues_celery_task(upload_deps):
    client.post(
        "/api/upload",
        files={
            "file": ("model.onnx", io.BytesIO(b"fake-onnx"), "application/octet-stream")
        },
        data={"email": "user@example.com", "language": "java", "experiment": "exp"},
    )

    upload_deps["task"].apply_async.assert_called_once()
    kwargs = upload_deps["task"].apply_async.call_args.kwargs
    assert kwargs["task_id"] == TASK_UID
    assert kwargs["args"] == [TASK_UID, "user@example.com", "exp", "model.onnx", "java"]


def test_upload_saves_file_via_handle_upload(upload_deps):
    client.post(
        "/api/upload",
        files={
            "file": ("model.onnx", io.BytesIO(b"fake-onnx"), "application/octet-stream")
        },
        data={"email": "user@example.com", "language": "csharp", "experiment": "exp"},
    )

    upload_deps["upload"].assert_called_once()
    args = upload_deps["upload"].call_args.args
    assert args[0] == TASK_UID
    assert args[2] == "csharp"


def test_ranking_returns_serialized_experiments():
    fake_exp = MagicMock(
        id=1,
        experiment_name="exp",
        model_name="model",
        email="u@e.com",
        total_tests=10,
        total_errors=1,
        mean_coverage=0.5,
        median_coverage=0.6,
        total_time_sec=10.0,
        methods_launched=5,
        methods_with_results=4,
        language="csharp",
        is_baseline=False,
        model_object_key="models/x",
        results_object_key="results/x",
        created_at="2025-01-01",
    )
    with patch("backend.main.get_all_experiments", return_value=[fake_exp]):
        resp = client.get("/api/ranking")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["experiment_name"] == "exp"
    assert data[0]["coverage_pct"] == 80.0


def test_ranking_by_language_filter():
    with patch(
        "backend.main.get_experiments_by_language", return_value=[]
    ) as mock_filtered:
        resp = client.get("/api/ranking?language=java")

    assert resp.status_code == 200
    mock_filtered.assert_called_once_with("java")


def test_ranking_all_uses_aggregated():
    with patch(
        "backend.main.get_aggregated_all_experiments", return_value=[]
    ) as mock_agg:
        resp = client.get("/api/ranking?language=all")

    assert resp.status_code == 200
    mock_agg.assert_called_once()


def test_status_returns_celery_state():
    fake_result = MagicMock(state="PENDING")
    with patch("backend.main.celery_app") as mock_celery:
        mock_celery.AsyncResult.return_value = fake_result
        resp = client.get(f"/api/status/{TASK_UID}")

    assert resp.status_code == 200
    assert resp.json() == {"status": "PENDING", "task_uid": TASK_UID}


def test_cancel_by_token_success():
    with (
        patch(
            "backend.main.verify_and_consume_cancel_token", return_value=True
        ) as mock_verify,
        patch("backend.main.celery_app") as mock_celery,
        patch("backend.main.subprocess.run") as mock_sp,
        patch("backend.main.shutil.rmtree"),
    ):
        resp = client.get(f"/api/cancel/{TASK_UID}?token=tok-xyz")

    assert resp.status_code == 200
    assert "Experiment cancelled" in resp.text
    mock_verify.assert_called_once_with(TASK_UID, "tok-xyz")
    mock_celery.control.revoke.assert_called_once_with(TASK_UID)
    mock_sp.assert_called_once()


def test_cancel_by_token_already_completed():
    with (
        patch("backend.main.verify_and_consume_cancel_token", return_value=False),
        patch("backend.main.is_task_completed", return_value=True),
    ):
        resp = client.get(f"/api/cancel/{TASK_UID}?token=any")

    assert resp.status_code == 200
    assert "already completed" in resp.text.lower()


def test_cancel_by_token_invalid():
    with (
        patch("backend.main.verify_and_consume_cancel_token", return_value=False),
        patch("backend.main.is_task_completed", return_value=False),
    ):
        resp = client.get(f"/api/cancel/{TASK_UID}?token=bad")

    assert resp.status_code == 400
    assert "invalid" in resp.text.lower()


def test_cancel_by_token_missing_token_returns_422():
    resp = client.get(f"/api/cancel/{TASK_UID}")
    assert resp.status_code == 422


def test_compare_starts_task_and_returns_uid(fake_uuid):
    exp1 = MagicMock(results_object_key="results/1", experiment_name="exp1")
    exp2 = MagicMock(results_object_key="results/2", experiment_name="exp2")

    with (
        patch("backend.main.get_experiment_by_id", side_effect=[exp1, exp2]),
        patch("backend.main.run_ranking_comparison_task") as mock_task,
    ):
        resp = client.post("/api/compare", json={"exp_id_1": 1, "exp_id_2": 2})

    assert resp.status_code == 200
    assert resp.json() == {"comparison_uid": TASK_UID}
    mock_task.apply_async.assert_called_once()
    kwargs = mock_task.apply_async.call_args.kwargs
    assert kwargs["task_id"] == TASK_UID
    assert kwargs["args"] == [TASK_UID, 1, 2]


def test_compare_returns_404_when_experiment_missing():
    with patch("backend.main.get_experiment_by_id", side_effect=[None, None]):
        resp = client.post("/api/compare", json={"exp_id_1": 1, "exp_id_2": 2})

    assert resp.status_code == 404


def test_compare_returns_422_when_no_results_object_key():
    exp1 = MagicMock(results_object_key=None)
    exp2 = MagicMock(results_object_key="results/2")

    with patch("backend.main.get_experiment_by_id", side_effect=[exp1, exp2]):
        resp = client.post("/api/compare", json={"exp_id_1": 1, "exp_id_2": 2})

    assert resp.status_code == 422


def test_compare_status_pending():
    fake_result = MagicMock(state="PENDING")
    with patch("backend.main.celery_app") as mock_celery:
        mock_celery.AsyncResult.return_value = fake_result
        resp = client.get(f"/api/compare/{COMPARISON_UID}/status")

    assert resp.status_code == 200
    assert resp.json() == {"status": "PENDING"}


def test_compare_status_success_returns_files():
    fake_result = MagicMock(state="SUCCESS")
    fake_result.get.return_value = [
        f"comparisons/{COMPARISON_UID}/plot.png",
        f"comparisons/{COMPARISON_UID}/report.pdf",
    ]
    with patch("backend.main.celery_app") as mock_celery:
        mock_celery.AsyncResult.return_value = fake_result
        resp = client.get(f"/api/compare/{COMPARISON_UID}/status")

    data = resp.json()
    assert resp.status_code == 200
    assert data["status"] == "SUCCESS"
    names = [f["name"] for f in data["files"]]
    assert names == ["plot.png", "report.pdf"]
    assert all(COMPARISON_UID in f["url"] for f in data["files"])


def test_compare_status_failure_returns_error():
    fake_result = MagicMock(state="FAILURE", info="boom")
    with patch("backend.main.celery_app") as mock_celery:
        mock_celery.AsyncResult.return_value = fake_result
        resp = client.get(f"/api/compare/{COMPARISON_UID}/status")

    assert resp.status_code == 200
    assert resp.json() == {"status": "FAILURE", "error": "boom"}


def test_post_cancel_returns_cancelled_status():
    with (
        patch("backend.main.celery_app"),
        patch("backend.main.subprocess.run"),
        patch("backend.main.shutil.rmtree"),
    ):
        resp = client.post(f"/api/cancel/{TASK_UID}")

    assert resp.status_code == 200
    assert resp.json() == {"status": "cancelled", "task_uid": TASK_UID}


def test_celery_task_not_actually_executed_by_api(upload_deps):
    client.post(
        "/api/upload",
        files={"file": ("model.onnx", io.BytesIO(b"x"), "application/octet-stream")},
        data={"email": "u@e.com", "language": "csharp", "experiment": "exp"},
    )

    task_module.process_and_cleanup_task.apply_async = (
        task_module.process_and_cleanup_task.apply_async
    )
    upload_deps["task"].apply_async.assert_called_once()
