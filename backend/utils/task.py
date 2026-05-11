import logging

from celery import Celery
from celery.signals import setup_logging

from backend.config.paths import (
    ARTIFACTS_AI_CSV_FILE,
    MODEL_ONNX_FILE,
    REDIS_URL,
    get_thread_filepath,
    get_tmp_thread_files,
)
from backend.db.repository import save_experiment
from backend.file_utils.files import reset_dirs
from backend.file_utils.runstrat_metrics import compute_metrics
from backend.storage.minio_client import upload_file
from backend.utils.docker_runner import run_pipeline
from backend.utils.results_sender import send_publish_results_by_email
from backend.utils.token_store import mark_task_completed

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    worker_hijack_root_logger=False,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@setup_logging.connect
def configure_logging(**__):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )


logger = logging.getLogger(__name__)


@celery_app.task
def process_and_cleanup_task(
    task_uid: str,
    email: str,
    experiment: str,
    filename: str,
):
    model_object_key = None
    results_object_key = None

    try:
        run_pipeline(task_uid)

        ai_csv_path = get_thread_filepath(task_uid, ARTIFACTS_AI_CSV_FILE)
        model_path = get_thread_filepath(task_uid, MODEL_ONNX_FILE)
        metrics = compute_metrics(ai_csv_path)

        try:
            model_object_key = upload_file(model_path, f"models/{task_uid}/model.onnx")
            results_object_key = upload_file(ai_csv_path, f"results/{task_uid}/AI.csv")
        except Exception:
            logger.exception("MinIO upload failed for task %s", task_uid)

        model_name = filename[:-5] if filename.endswith(".onnx") else filename
        try:
            save_experiment(
                experiment_name=experiment,
                model_name=model_name,
                email=email,
                metrics=metrics,
                model_object_key=model_object_key,
                results_object_key=results_object_key,
            )
        except Exception:
            logger.exception("DB save failed for task %s", task_uid)

        send_publish_results_by_email(email, metrics, experiment, filename)
    except Exception:
        logger.exception("Task %s failed", task_uid)

    finally:
        try:
            mark_task_completed(task_uid)
            reset_dirs(get_tmp_thread_files(task_uid))
        except Exception:
            logger.warning("Cleanup failed for %s", task_uid)
