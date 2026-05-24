import os
import shutil

from fastapi import UploadFile

from backend.config.paths import (
    CPP_LAUNCH_INFO_FILE,
    CSHARP_LAUNCH_INFO_FILE,
    JAVA_LAUNCH_INFO_FILE,
    LAUNCH_INFO_FILE,
    MODEL_ONNX_FILE,
    get_thread_filepath,
)
from backend.file_utils.files import save_upload_file

LANGUAGE_CSVS: dict[str, str] = {
    "csharp": CSHARP_LAUNCH_INFO_FILE,
    "java": JAVA_LAUNCH_INFO_FILE,
    "cpp": CPP_LAUNCH_INFO_FILE,
}


def handle_upload(uid: str, file: UploadFile, language: str) -> None:
    save_upload_file(file, get_thread_filepath(uid, MODEL_ONNX_FILE))

    if language != "all":
        csv_src = LANGUAGE_CSVS[language]
        dest = get_thread_filepath(uid, LAUNCH_INFO_FILE)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(csv_src, dest)
