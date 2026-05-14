import io
import mimetypes
import shutil
import subprocess
import zipfile

import shortuuid
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from backend.config.paths import BASE_URL, FRONTEND_URL, get_tmp_thread_files
from backend.db.database import Base, engine
from backend.db.models import Experiment  # noqa: F401 — registers the table
from backend.db.repository import (
    get_aggregated_all_experiments,
    get_all_experiments,
    get_experiment_by_id,
    get_experiments_by_language,
)
from backend.storage.minio_client import stream_object
from backend.utils.data_uploader import handle_upload
from backend.utils.results_sender import send_task_started_email
from backend.utils.task import (
    celery_app,
    process_and_cleanup_task,
    run_ranking_comparison_task,
)
from backend.utils.token_store import (
    generate_cancel_token,
    is_task_completed,
    verify_and_consume_cancel_token,
)

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
    language: str = Form(...),
    experiment: str = Form(...),
):
    task_uid = str(shortuuid.uuid())

    handle_upload(task_uid, file, language)
    process_and_cleanup_task.apply_async(
        args=[task_uid, email, experiment, file.filename, language],
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
        "language": language,
        "message": "Data uploaded, processing started",
    }


def _experiment_to_dict(e) -> dict:
    coverage_pct = (
        round(e.methods_with_results / e.methods_launched * 100, 1)
        if e.methods_launched and e.methods_with_results is not None
        else None
    )
    return {
        "id": e.id,
        "experiment_name": e.experiment_name,
        "model_name": e.model_name,
        "email": e.email,
        "total_tests": e.total_tests,
        "total_errors": e.total_errors,
        "mean_coverage": e.mean_coverage,
        "median_coverage": e.median_coverage,
        "total_time_sec": e.total_time_sec,
        "methods_launched": e.methods_launched,
        "methods_with_results": e.methods_with_results,
        "coverage_pct": coverage_pct,
        "language": e.language,
        "is_baseline": e.is_baseline,
        "model_object_key": e.model_object_key,
        "results_object_key": e.results_object_key,
        "created_at": e.created_at,
    }


@app.get("/api/ranking")
async def get_ranking(language: str | None = None):
    if language == "all":
        rows = get_aggregated_all_experiments()
        return [_experiment_to_dict(r) for r in rows]
    if language in ("csharp", "java", "cpp"):
        rows = get_experiments_by_language(language)
    else:
        rows = get_all_experiments()
    return [_experiment_to_dict(e) for e in rows]


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


class CompareRequest(BaseModel):
    exp_id_1: int
    exp_id_2: int


@app.post("/api/compare")
async def start_comparison(req: CompareRequest):
    exp1 = get_experiment_by_id(req.exp_id_1)
    exp2 = get_experiment_by_id(req.exp_id_2)
    if not exp1 or not exp2:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Experiment not found")
    if not exp1.results_object_key or not exp2.results_object_key:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="One or both experiments have no results stored in MinIO",
        )

    comparison_uid = str(shortuuid.uuid())
    run_ranking_comparison_task.apply_async(
        args=[comparison_uid, req.exp_id_1, req.exp_id_2],
        task_id=comparison_uid,
        queue="celery",
    )
    return {"comparison_uid": comparison_uid}


@app.get("/api/compare/{comparison_uid}/status")
async def get_comparison_status(comparison_uid: str):
    result = celery_app.AsyncResult(comparison_uid)
    if result.state == "SUCCESS":
        image_keys: list[str] = result.get()
        files = [
            {
                "name": key.split("/")[-1],
                "url": f"{BASE_URL}/api/compare/{comparison_uid}/file/{key.split('/')[-1]}",
            }
            for key in image_keys
        ]
        return {"status": "SUCCESS", "files": files}
    if result.state == "FAILURE":
        return {"status": "FAILURE", "error": str(result.info)}
    return {"status": result.state}


@app.get("/api/compare/{comparison_uid}/file/{filename}")
async def proxy_comparison_file(comparison_uid: str, filename: str):
    object_key = f"comparisons/{comparison_uid}/{filename}"
    try:
        stream = stream_object(object_key)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found") from None
    media_type, _ = mimetypes.guess_type(filename)
    media_type = media_type or "application/octet-stream"
    return StreamingResponse(
        stream,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@app.get("/api/compare/{comparison_uid}/files.zip")
async def download_comparison_zip(comparison_uid: str):
    result = celery_app.AsyncResult(comparison_uid)
    if result.state != "SUCCESS":
        raise HTTPException(status_code=404, detail="Comparison not ready")

    image_keys: list[str] = result.get()
    pdf_keys = [k for k in image_keys if k.lower().endswith(".pdf")]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for key in pdf_keys:
            fname = key.split("/")[-1]
            obj = stream_object(key)
            try:
                zf.writestr(fname, obj.read())
            finally:
                obj.close()
                obj.release_conn()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="comparison_{comparison_uid[:8]}.zip"'
        },
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
