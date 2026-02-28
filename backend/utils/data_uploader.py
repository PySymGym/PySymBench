import json
from collections import defaultdict

from fastapi import UploadFile

from backend.file_utils.csv_methods_writer import write_launch_info_to_csv
from backend.file_utils.files import save_upload_file
from backend.utils.methods_handler import Methods
from backend.config.paths import LAUNCH_INFO_FILE, MODEL_ONNX_FILE, get_thread_filepath


def handle_upload(
    uid: str,
    file: UploadFile,
    methods: str,
    dataset_dll_and_methods: defaultdict,
) -> None:
    launch_methods = Methods.get_launch_info_list_from_selected(
        dataset_dll_and_methods, json.loads(methods)
    )

    save_upload_file(file, get_thread_filepath(uid, MODEL_ONNX_FILE))

    write_launch_info_to_csv(
        parsed_methods=launch_methods,
        output_file=get_thread_filepath(uid, LAUNCH_INFO_FILE),
    )
