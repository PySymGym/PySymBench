import json

from backend.file_utils.csv_methods_writer import write_launch_info_csv
from backend.file_utils.files import save_upload_file
from backend.utils.methods_handler import Methods
from backend.config.paths import LAUNCH_INFO_FILE, MODEL_ONNX_FILE, get_process_filepath


def handle_upload(
        uid,
        file,
        methods: str,
        dataset_methods: Methods,
) -> None:
    selection_methods = json.loads(methods)

    save_upload_file(file, get_process_filepath(uid, MODEL_ONNX_FILE))

    write_launch_info_csv(
        methods=selection_methods,
        dataset_methods=dataset_methods,
        output_file=get_process_filepath(uid, LAUNCH_INFO_FILE),
    )
