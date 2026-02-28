import os
import shutil
from fastapi import UploadFile


def save_upload_file(file: UploadFile, dest_filepath: str) -> None:
    os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)
    with open(dest_filepath, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            f.write(chunk)


def reset_dirs(paths: list) -> None:
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
