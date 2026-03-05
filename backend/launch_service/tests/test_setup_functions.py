import os
from unittest.mock import Mock, patch

from backend.config.paths import DOCKER_DIR, RESOURCES_DIR
from backend.launch_service.app_setup import fetch_dataset, IMAGE_NAME, build_container


def test_fetch_dataset(tmp_path):
    url = "https://example.com/dataset.csv"
    test_content = b"dll,method\nManuallyCollected.dll,BinSearchMain"
    data_file = tmp_path / "dataset.json"

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.content = test_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_dataset(url, data_file)

    assert result == data_file
    assert os.path.exists(data_file)
    with open(data_file, "rb") as f:
        assert f.read() == test_content
    mock_get.assert_called_once_with(url)
    mock_response.raise_for_status.assert_called_once()


def test_successful_build():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)

        with patch("os.makedirs") as mock_makedirs:
            build_container()

    expected_command = ["docker", "build", "--no-cache", "-t", IMAGE_NAME, DOCKER_DIR]
    mock_run.assert_called_once_with(expected_command, check=True)
    mock_makedirs.assert_called_once_with(RESOURCES_DIR, exist_ok=True)
