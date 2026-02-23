import json

from backend.file_utils.csv_methods_writer import write_launch_info_csv
from backend.file_utils.files import save_upload_file, reset_dir
from backend.utils.methods_handler import Methods
from backend.config.paths import LAUNCH_INFO_FILE, MODEL_ONNX_FILE, RESULTS_DIR


def handle_upload(
    file,
    methods: str,
    dataset_methods: Methods,
) -> None:
    selection_methods = json.loads(methods)
    if not isinstance(selection_methods, list):
        selection_methods = []

    save_upload_file(file, MODEL_ONNX_FILE)

    write_launch_info_csv(
        methods=selection_methods,
        dataset_methods=dataset_methods,
        output_file=LAUNCH_INFO_FILE,
    )

    reset_dir(RESULTS_DIR)
