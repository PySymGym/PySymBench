import subprocess
from unittest.mock import call, patch

import pytest
from fastapi.testclient import TestClient

from backend.config.paths import get_tmp_thread_files
from backend.main import app

client = TestClient(app)

TASK_UID = "abc123"


@pytest.fixture
def mock_cancel_deps():
    """Patch all three side-effects of the cancel endpoint."""
    with (
        patch("backend.main.celery_app") as mock_celery,
        patch("backend.main.subprocess.run") as mock_subproc,
        patch("backend.main.shutil.rmtree") as mock_rmtree,
    ):
        yield {
            "celery": mock_celery,
            "subprocess": mock_subproc,
            "rmtree": mock_rmtree,
        }


def test_cancel_returns_200(mock_cancel_deps):
    response = client.post(f"/api/cancel/{TASK_UID}")
    assert response.status_code == 200


def test_cancel_response_body(mock_cancel_deps):
    response = client.post(f"/api/cancel/{TASK_UID}")
    data = response.json()
    assert data["status"] == "cancelled"
    assert data["task_uid"] == TASK_UID


def test_cancel_revokes_celery_task(mock_cancel_deps):
    client.post(f"/api/cancel/{TASK_UID}")
    mock_cancel_deps["celery"].control.revoke.assert_called_once_with(TASK_UID)


def test_cancel_stops_docker_container(mock_cancel_deps):
    client.post(f"/api/cancel/{TASK_UID}")
    mock_cancel_deps["subprocess"].assert_called_once_with(
        ["docker", "stop", f"pysymbench-{TASK_UID}"],
        check=False,
        capture_output=True,
        timeout=30,
    )


def test_cancel_removes_all_tmp_dirs(mock_cancel_deps):
    client.post(f"/api/cancel/{TASK_UID}")
    expected_paths = get_tmp_thread_files(TASK_UID)
    calls = [call(p, ignore_errors=True) for p in expected_paths]
    mock_cancel_deps["rmtree"].assert_has_calls(calls, any_order=True)
    assert mock_cancel_deps["rmtree"].call_count == len(expected_paths)


def test_cancel_still_succeeds_when_docker_stop_fails(mock_cancel_deps):
    """docker stop returning non-zero exit (container not running) must not raise."""
    mock_cancel_deps["subprocess"].return_value = subprocess.CompletedProcess(
        args=[], returncode=1
    )
    response = client.post(f"/api/cancel/{TASK_UID}")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_different_uids_use_correct_container_name(mock_cancel_deps):
    for uid in ["uid-one", "uid-two"]:
        mock_cancel_deps["subprocess"].reset_mock()
        client.post(f"/api/cancel/{uid}")
        args = mock_cancel_deps["subprocess"].call_args[0][0]
        assert args[-1] == f"pysymbench-{uid}"
