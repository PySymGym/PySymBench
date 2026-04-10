import shortuuid
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.config.paths import METHODS_TS_FILE
from backend.utils.data_uploader import handle_upload
from backend.utils.methods_handler import Methods
from backend.utils.task import process_and_cleanup_task

DATASET_DLLS_AND_METHODS = Methods.parse_frontend_file_to_dll_methods(METHODS_TS_FILE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def handle_submit(
    file: UploadFile,
    email: str = Form(...),
    methods: str = Form(...),
    experiment: str = Form(...),
):
    task_uid = str(shortuuid.uuid())

    handle_upload(task_uid, file, methods, DATASET_DLLS_AND_METHODS)
    process_and_cleanup_task.delay(task_uid, email, experiment, file.filename)

    return {
        "task_uid": task_uid,
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "methods": methods,
        "message": "Data uploaded, processing started",
    }
