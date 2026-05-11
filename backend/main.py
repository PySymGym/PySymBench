import shutil
import subprocess

import shortuuid
from fastapi import BackgroundTasks, FastAPI, Form, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.config.paths import (
    BASE_URL,
    FRONTEND_URL,
    METHODS_TS_FILE,
    get_tmp_thread_files,
)
from backend.db.database import Base, engine
from backend.db.models import Experiment  # noqa: F401 — registers the table
from backend.db.repository import get_all_experiments
from backend.utils.data_uploader import handle_upload
from backend.utils.methods_handler import Methods
from backend.utils.results_sender import send_task_started_email
from backend.utils.task import celery_app, process_and_cleanup_task
from backend.utils.token_store import (
    generate_cancel_token,
    is_task_completed,
    verify_and_consume_cancel_token,
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
    background_tasks: BackgroundTasks,
    file: UploadFile,
    email: str = Form(...),
    methods: str = Form(...),
    experiment: str = Form(...),
):
    task_uid = str(shortuuid.uuid())

    handle_upload(task_uid, file, methods, DATASET_DLLS_AND_METHODS)
    process_and_cleanup_task.apply_async(
        args=[task_uid, email, experiment, file.filename],
        task_id=task_uid,
        queue="celery",
    )

    cancel_token = generate_cancel_token(task_uid)
    cancel_url = f"{BASE_URL}/api/cancel/{task_uid}?token={cancel_token}"
    background_tasks.add_task(
        send_task_started_email, email, experiment, file.filename, cancel_url
    )

    return {
        "task_uid": task_uid,
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "methods": methods,
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
            "is_baseline": e.is_baseline,
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


def _cancel_html(title: str, message: str, success: bool) -> str:
    color = "#52c41a" if success else "#ff4d4f"
    icon = "✓" if success else "✗"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           display: flex; align-items: center; justify-content: center;
           min-height: 100vh; margin: 0; background: #f5f5f5; }}
    .card {{ background: #fff; border-radius: 8px; padding: 48px 64px;
             box-shadow: 0 2px 12px rgba(0,0,0,.1); text-align: center; max-width: 480px; }}
    .icon {{ font-size: 48px; color: {color}; margin-bottom: 16px; }}
    h1 {{ font-size: 22px; color: #1a1a1a; margin: 0 0 12px; }}
    p {{ color: #595959; margin: 0 0 24px; }}
    a {{ color: #1677ff; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{message}</p>
    <a href="{FRONTEND_URL}">Return to PySymBench</a>
  </div>
</body>
</html>"""


@app.get("/api/cancel/{task_uid}", response_class=HTMLResponse)
async def cancel_task_by_link(task_uid: str, token: str = Query(...)):
    if not verify_and_consume_cancel_token(task_uid, token):
        if is_task_completed(task_uid):
            return HTMLResponse(
                content=_cancel_html(
                    "Experiment already completed",
                    "This experiment has already finished — the results have been sent to your email.",
                    success=False,
                )
            )
        return HTMLResponse(
            content=_cancel_html(
                "Link invalid or expired",
                "This cancellation link is invalid or has already been used.",
                success=False,
            ),
            status_code=400,
        )

    celery_app.control.revoke(task_uid)
    subprocess.run(
        ["docker", "stop", f"pysymbench-{task_uid}"],
        check=False,
        capture_output=True,
        timeout=30,
    )
    for path in get_tmp_thread_files(task_uid):
        shutil.rmtree(path, ignore_errors=True)

    return HTMLResponse(
        content=_cancel_html(
            "Experiment cancelled",
            "Your experiment has been successfully cancelled.",
            success=True,
        )
    )


@app.post("/api/cancel/{task_uid}")
async def cancel_task(task_uid: str):
    celery_app.control.revoke(task_uid)

    subprocess.run(
        ["docker", "stop", f"pysymbench-{task_uid}"],
        check=False,
        capture_output=True,
        timeout=30,
    )

    for path in get_tmp_thread_files(task_uid):
        shutil.rmtree(path, ignore_errors=True)

    return {"status": "cancelled", "task_uid": task_uid}
