import os
import shutil
from fastapi import UploadFile


def save_upload_file(file: UploadFile, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            f.write(chunk)


def reset_dirs(paths: list) -> None:
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
