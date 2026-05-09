import json
import os
import shutil
from collections import defaultdict

from fastapi import UploadFile

from backend.config.paths import (
    LAUNCH_INFO_FILE,
    MODEL_ONNX_FILE,
    RANKING_LAUNCH_INFO_FILE,
    get_thread_filepath,
)
from backend.file_utils.csv_methods_writer import write_launch_info_to_csv
from backend.file_utils.files import save_upload_file
from backend.utils.methods_handler import Methods


def handle_upload(
    uid: str,
    file: UploadFile,
    methods: str,
    dataset_dll_and_methods: defaultdict,
) -> None:
    launch_methods = Methods.expand_selected_items_to_methods(
        dataset_dll_and_methods, json.loads(methods)
    )

    save_upload_file(file, get_thread_filepath(uid, MODEL_ONNX_FILE))

    write_launch_info_to_csv(
        parsed_methods=launch_methods,
        output_file=get_thread_filepath(uid, LAUNCH_INFO_FILE),
    )


def handle_ranking_upload(uid: str, file: UploadFile) -> None:
    save_upload_file(file, get_thread_filepath(uid, MODEL_ONNX_FILE))

    dest = get_thread_filepath(uid, LAUNCH_INFO_FILE)

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    shutil.copy2(RANKING_LAUNCH_INFO_FILE, dest)
