import pytest
import zipfile
from unittest.mock import Mock, patch, mock_open, call

from backend.utils.results_sender import send_folder_by_email, require_env


def test_require_env_success(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "test_value")
    assert require_env("TEST_VAR") == "test_value"


def test_require_env_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(
        RuntimeError, match="Environment variable MISSING_VAR is not set"
    ):
        require_env("MISSING_VAR")


def test_send_folder_by_email_folder_not_found():
    with pytest.raises(ValueError, match="Folder not found: /nonexistent/path"):
        send_folder_by_email(
            to_email="test@example.com",
            folder_path="/nonexistent/path",
            experiment_name="test_exp",
            model_file_name="model.onnx",
        )


@patch("backend.utils.results_sender.load_dotenv")
@patch("backend.utils.results_sender.require_env")
@patch("backend.utils.results_sender.smtplib.SMTP")
@patch("backend.utils.results_sender.os.remove")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake zip content")
def test_send_folder_by_email_success(
    mock_file_open,
    mock_remove,
    mock_smtp,
    mock_require_env,
    mock_load_dotenv,
    tmp_path,
):
    mock_require_env.side_effect = ["sender@gmail.com", "app_password"]

    test_folder = tmp_path / "test_results"
    test_folder.mkdir()
    (test_folder / "file1.txt").write_text("content1")
    (test_folder / "file2.txt").write_text("content2")
    (test_folder / "subfolder").mkdir()
    (test_folder / "subfolder" / "file3.txt").write_text("content3")

    mock_server_instance = Mock()
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    send_folder_by_email(
        to_email="recipient@example.com",
        folder_path=str(test_folder),
        experiment_name="test_experiment",
        model_file_name="model.onnx",
    )

    mock_load_dotenv.assert_called_once()
    assert mock_require_env.call_count == 2
    mock_require_env.assert_has_calls([call("EMAIL"), call("APP_PASSWORD")])

    zip_path = test_folder.with_suffix(".zip")
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as zipf:
        file_list = zipf.namelist()
        assert "file1.txt" in file_list
        assert "file2.txt" in file_list
        assert "subfolder/file3.txt" in file_list

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=30)
    mock_server_instance.ehlo.assert_called()
    mock_server_instance.starttls.assert_called_once()
    mock_server_instance.login.assert_called_once_with(
        "sender@gmail.com", "app_password"
    )
    mock_server_instance.send_message.assert_called_once()

    mock_remove.assert_called_once()
    called_args = mock_remove.call_args[0][0]
    assert str(called_args) == str(test_folder) + ".zip"


@patch("backend.utils.results_sender.load_dotenv")
@patch("backend.utils.results_sender.require_env")
@patch("backend.utils.results_sender.smtplib.SMTP")
@patch("backend.utils.results_sender.os.remove")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake zip content")
def test_send_folder_by_email_smtp_error(
    mock_file_open,
    mock_remove,
    mock_smtp,
    mock_require_env,
    mock_load_dotenv,
    tmp_path,
):
    mock_require_env.side_effect = ["sender@gmail.com", "app_password"]

    test_folder = tmp_path / "test_results"
    test_folder.mkdir()
    (test_folder / "file.txt").write_text("content")

    mock_server_instance = Mock()
    mock_server_instance.send_message.side_effect = Exception("SMTP Error")
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    with pytest.raises(Exception, match="SMTP Error"):
        send_folder_by_email(
            to_email="recipient@example.com",
            folder_path=str(test_folder),
            experiment_name="test_experiment",
            model_file_name="model.onnx",
        )

    mock_remove.assert_called_once()
    called_args = mock_remove.call_args[0][0]
    assert str(called_args) == str(test_folder) + ".zip"


@patch("backend.utils.results_sender.load_dotenv")
@patch("backend.utils.results_sender.require_env")
@patch("backend.utils.results_sender.smtplib.SMTP")
@patch("backend.utils.results_sender.os.remove")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake zip content")
def test_send_folder_by_email_empty_folder(
    mock_file_open,
    mock_remove,
    mock_smtp,
    mock_require_env,
    mock_load_dotenv,
    tmp_path,
):
    mock_require_env.side_effect = ["sender@gmail.com", "app_password"]

    test_folder = tmp_path / "empty_results"
    test_folder.mkdir()

    mock_server_instance = Mock()
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    send_folder_by_email(
        to_email="recipient@example.com",
        folder_path=str(test_folder),
        experiment_name="test_experiment",
        model_file_name="model.onnx",
    )

    mock_remove.assert_called_once()
    called_args = mock_remove.call_args[0][0]
    assert str(called_args) == str(test_folder) + ".zip"
    mock_server_instance.send_message.assert_called_once()


@patch("backend.utils.results_sender.load_dotenv")
@patch("backend.utils.results_sender.require_env")
@patch("backend.utils.results_sender.smtplib.SMTP")
def test_send_folder_by_email_special_characters(
    mock_smtp, mock_require_env, mock_load_dotenv, tmp_path
):
    mock_require_env.side_effect = ["sender@gmail.com", "app_password"]

    test_folder = tmp_path / "test_результаты_测试"
    test_folder.mkdir()
    (test_folder / "file_テスト.txt").write_text("content")

    mock_server_instance = Mock()
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    with patch("builtins.open", mock_open(read_data=b"zip content")):
        send_folder_by_email(
            to_email="recipient@example.com",
            folder_path=str(test_folder),
            experiment_name="Эксперимент_测试",
            model_file_name="модель.pkl",
        )

    mock_server_instance.send_message.assert_called_once()
    call_args = mock_server_instance.send_message.call_args[0][0]
    assert "Эксперимент_测试" in call_args["Subject"]


def test_integration_with_real_files(tmp_path):
    test_folder = tmp_path / "integration_test"
    test_folder.mkdir()
    (test_folder / "result1.txt").write_text("test data 1")
    (test_folder / "result2.txt").write_text("test data 2")

    zip_path = test_folder.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in test_folder.rglob("*"):
            zipf.write(file, file.relative_to(test_folder))

    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as zipf:
        file_list = zipf.namelist()
        assert "result1.txt" in file_list
        assert "result2.txt" in file_list

    zip_path.unlink()


@patch("backend.utils.results_sender.load_dotenv")
@patch("backend.utils.results_sender.require_env")
@patch("backend.utils.results_sender.smtplib.SMTP")
def test_email_content_structure(
    mock_smtp, mock_require_env, mock_load_dotenv, tmp_path
):
    mock_require_env.side_effect = ["sender@gmail.com", "app_password"]

    test_folder = tmp_path / "test_results"
    test_folder.mkdir()
    (test_folder / "file.txt").write_text("content")

    mock_server_instance = Mock()
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    with patch("builtins.open", mock_open(read_data=b"zip content")):
        send_folder_by_email(
            to_email="recipient@example.com",
            folder_path=str(test_folder),
            experiment_name="test_exp",
            model_file_name="model.onnx",
        )

    sent_msg = mock_server_instance.send_message.call_args[0][0]

    assert sent_msg["From"] == "sender@gmail.com"
    assert sent_msg["To"] == "recipient@example.com"
    assert sent_msg["Subject"] == "Results of test_exp with model"

    assert len(sent_msg.get_payload()) == 2

    attachment = sent_msg.get_payload()[1]
    assert attachment.get_content_type() == "application/zip"
    assert attachment.get_filename() == "results"
