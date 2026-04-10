import subprocess
from unittest.mock import Mock, patch

from backend.config.paths import DOCKER_DIR, RESOURCES_DIR
from backend.launch_service.app_setup import IMAGE_NAME, build_container, fetch_dataset


def test_fetch_dataset_success(tmp_path, monkeypatch):
    test_file = tmp_path / "dataset.json"
    commands_executed = []

    class MockResult:
        def __init__(self, returncode=0, stdout=b"", stderr=b""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def mock_subprocess_run(*args, **kwargs):
        commands_executed.append(args[0])

        if args[0][0] == "docker" and args[0][1] == "cp":
            test_file.write_text('{"test": "data"}')

        return MockResult()

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    result = fetch_dataset(str(test_file))

    assert result == str(test_file)
    assert test_file.exists()
    assert test_file.read_text() == '{"test": "data"}'
    assert len(commands_executed) == 3
    assert commands_executed[0][:3] == ["docker", "create", "--name"]
    assert commands_executed[1][:2] == ["docker", "cp"]
    assert commands_executed[2][:2] == ["docker", "rm"]


def test_successful_build():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)

        with patch("os.makedirs") as mock_makedirs:
            build_container()

    expected_command = ["docker", "build", "--no-cache", "-t", IMAGE_NAME, DOCKER_DIR]
    mock_run.assert_called_once_with(expected_command, check=True)
    mock_makedirs.assert_called_once_with(RESOURCES_DIR, exist_ok=True)
