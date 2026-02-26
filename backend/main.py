from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shortuuid

from backend.file_utils.files import reset_dirs
from backend.utils.docker_runner import run_pipeline
from backend.utils.data_uploader import handle_upload
from backend.utils.methods_handler import Methods
from backend.utils.results_sender import send_folder_by_email
from backend.config.paths import (
    RESULTS_DIR,
    DATASET_FILE,
    METHODS_TS_FILE,
    get_thread_filepath,
    get_tmp_thread_files
)

dataset_methods = Methods(data_filepath=DATASET_FILE, output_filepath=METHODS_TS_FILE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def handle_submit(
        file: UploadFile = File(...),
        email: str = Form(...),
        methods: str = Form(...),
        experiment: str = Form(...),
):
    task_uid = str(shortuuid.uuid())

    handle_upload(task_uid, file, methods, dataset_methods)

    run_pipeline(task_uid)

    send_folder_by_email(
        email,
        get_thread_filepath(task_uid, RESULTS_DIR),
        experiment,
        file.filename,
    )

    tmp_thread_dirs = get_tmp_thread_files(task_uid)
    reset_dirs(tmp_thread_dirs)

    return {
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "methods": methods,
        "message": "Data successfully uploaded",
    }
