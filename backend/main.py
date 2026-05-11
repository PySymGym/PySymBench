import shutil
import subprocess

import shortuuid
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.config.paths import METHODS_TS_FILE, get_tmp_thread_files
from backend.db.database import Base, engine
from backend.db.models import Experiment  # noqa: F401 — registers the table
from backend.db.repository import get_all_experiments
from backend.utils.data_uploader import handle_ranking_upload, handle_upload
from backend.utils.methods_handler import Methods
from backend.utils.task import (
    celery_app,
    process_and_cleanup_task,
    publish_and_cleanup_task,
)

DATASET_DLLS_AND_METHODS = Methods.parse_frontend_file_to_dll_methods(METHODS_TS_FILE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.post("/api/upload")
async def handle_submit(
    file: UploadFile,
    email: str = Form(...),
    methods: str = Form(...),
    experiment: str = Form(...),
    file2: UploadFile | None = None,
    comparison_mode: str = Form("baseline"),
):
    task_uid = str(shortuuid.uuid())

    handle_upload(task_uid, file, methods, DATASET_DLLS_AND_METHODS, file2)
    process_and_cleanup_task.apply_async(
        args=[
            task_uid,
            email,
            experiment,
            file.filename,
            comparison_mode,
            file2.filename if file2 else None,
        ],
        task_id=task_uid,
        queue="celery",
    )

    return {
        "task_uid": task_uid,
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "methods": methods,
        "message": "Data uploaded, processing started",
    }


@app.post("/api/ranking-upload")
async def handle_ranking_submit(
    file: UploadFile,
    email: str = Form(...),
    experiment: str = Form(...),
):
    task_uid = str(shortuuid.uuid())

    handle_ranking_upload(task_uid, file)
    publish_and_cleanup_task.apply_async(
        args=[task_uid, email, experiment, file.filename],
        task_id=task_uid,
        queue="celery",
    )

    return {
        "task_uid": task_uid,
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "message": "Data uploaded, processing started",
    }


@app.get("/api/ranking")
async def get_ranking():
    experiments = get_all_experiments()
    return [
        {
            "id": e.id,
            "experiment_name": e.experiment_name,
            "model_name": e.model_name,
            "email": e.email,
            "total_tests": e.total_tests,
            "total_errors": e.total_errors,
            "mean_coverage": e.mean_coverage,
            "median_coverage": e.median_coverage,
            "total_time_sec": e.total_time_sec,
            "model_object_key": e.model_object_key,
            "results_object_key": e.results_object_key,
            "created_at": e.created_at,
        }
        for e in experiments
    ]


@app.get("/api/status/{task_uid}")
async def get_task_status(task_uid: str):
    result = celery_app.AsyncResult(task_uid)
    return {"status": result.state, "task_uid": task_uid}


@app.post("/api/cancel/{task_uid}")
async def cancel_task(task_uid: str):
    # Revoke the task if still queued (prevents worker from starting it)
    celery_app.control.revoke(task_uid)

    # Stop the Docker container if the task is already running
    subprocess.run(
        ["docker", "stop", f"pysymbench-{task_uid}"],
        check=False,
        capture_output=True,
        timeout=30,
    )

    # Clean up temp files (safe to call even if worker already cleaned up)
    for path in get_tmp_thread_files(task_uid):
        shutil.rmtree(path, ignore_errors=True)

    return {"status": "cancelled", "task_uid": task_uid}
