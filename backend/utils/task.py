import csv as csv_module
import logging
import os
import shutil

from celery import Celery
from celery.signals import setup_logging

from backend.config.paths import (
    CPP_LAUNCH_INFO_FILE,
    CSHARP_LAUNCH_INFO_FILE,
    JAVA_LAUNCH_INFO_FILE,
    LAUNCH_INFO_FILE,
    MODEL_ONNX_FILE,
    REDIS_URL,
    RESULTS_DIR,
    get_thread_filepath,
    get_tmp_thread_files,
)
from backend.db.repository import save_experiment
from backend.file_utils.files import reset_dirs
from backend.file_utils.runstrat_metrics import (
    RunstratMetrics,
    combine_metrics,
    compute_metrics,
)
from backend.storage.minio_client import upload_file
from backend.utils.docker_runner import run_pipeline
from backend.utils.results_sender import send_experiment_results_by_email
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

LANGUAGE_CSVS: dict[str, str] = {
    "csharp": CSHARP_LAUNCH_INFO_FILE,
    "java": JAVA_LAUNCH_INFO_FILE,
    "cpp": CPP_LAUNCH_INFO_FILE,
}


def _ai_csv_path(task_uid: str, suffix: str) -> str:
    results_dir = get_thread_filepath(task_uid, RESULTS_DIR)
    return os.path.join(results_dir, f"artifacts_run_ai{suffix}", "AI.csv")


def _count_methods_in_csv(csv_path: str) -> int:
    with open(csv_path, newline="") as f:
        reader = csv_module.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


@celery_app.task
def process_and_cleanup_task(
    task_uid: str,
    email: str,
    experiment: str,
    filename: str,
    language: str,
):
    langs_to_run = ["csharp", "java", "cpp"] if language == "all" else [language]
    model_name = filename[:-5] if filename.endswith(".onnx") else filename
    model_path = get_thread_filepath(task_uid, MODEL_ONNX_FILE)
    metrics_by_lang: dict[str, RunstratMetrics] = {}

    try:
        model_object_key = None
        try:
            model_object_key = upload_file(model_path, f"models/{task_uid}/model.onnx")
        except Exception:
            logger.exception("MinIO model upload failed for task %s", task_uid)

        for lang in langs_to_run:
            try:
                csv_src = LANGUAGE_CSVS[lang]
                dest = get_thread_filepath(task_uid, LAUNCH_INFO_FILE)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(csv_src, dest)

                methods_launched = _count_methods_in_csv(csv_src)
                suffix = f"_{lang}"
                run_pipeline(task_uid, out_suffix=suffix)

                ai_csv = _ai_csv_path(task_uid, suffix)
                metrics = compute_metrics(ai_csv)
                metrics_by_lang[lang] = metrics

                results_object_key = None
                try:
                    results_object_key = upload_file(
                        ai_csv, f"results/{task_uid}/{lang}/AI.csv"
                    )
                except Exception:
                    logger.exception(
                        "MinIO results upload failed for task %s lang %s",
                        task_uid,
                        lang,
                    )

                try:
                    save_experiment(
                        experiment_name=experiment,
                        model_name=model_name,
                        email=email,
                        metrics=metrics,
                        methods_launched=methods_launched,
                        language=lang,
                        model_object_key=model_object_key,
                        results_object_key=results_object_key,
                    )
                except Exception:
                    logger.exception(
                        "DB save failed for task %s lang %s", task_uid, lang
                    )
            except Exception:
                logger.exception("Pipeline failed for task %s lang %s", task_uid, lang)

        if language == "all" and len(metrics_by_lang) >= 1:
            all_ai_csvs = [
                _ai_csv_path(task_uid, f"_{lang}")
                for lang in langs_to_run
                if lang in metrics_by_lang
            ]
            try:
                combined = combine_metrics(all_ai_csvs)
                total_launched = sum(
                    _count_methods_in_csv(LANGUAGE_CSVS[lang])
                    for lang in langs_to_run
                    if lang in metrics_by_lang
                )
                save_experiment(
                    experiment_name=experiment,
                    model_name=model_name,
                    email=email,
                    metrics=combined,
                    methods_launched=total_launched,
                    language="all",
                    model_object_key=model_object_key,
                )
            except Exception:
                logger.exception("Aggregated DB save failed for task %s", task_uid)

        send_experiment_results_by_email(email, metrics_by_lang, experiment, filename)
    except Exception:
        logger.exception("Task %s failed", task_uid)

    finally:
        try:
            mark_task_completed(task_uid)
            reset_dirs(get_tmp_thread_files(task_uid))
        except Exception:
            logger.warning("Cleanup failed for %s", task_uid)
