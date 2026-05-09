import logging

from celery import Celery
from celery.signals import setup_logging

from backend.config.paths import RESULTS_DIR, get_thread_filepath, get_tmp_thread_files
from backend.file_utils.files import reset_dirs
from backend.utils.docker_runner import run_pipeline
from backend.utils.results_sender import send_folder_by_email

celery_app = Celery(
    "tasks", broker="redis://localhost:6379", backend="redis://localhost:6379"
)

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
    try:
        run_pipeline(task_uid)
        send_folder_by_email(
            email,
            get_thread_filepath(task_uid, RESULTS_DIR),
            experiment,
            filename,
        )
    except Exception:
        logger.exception("Task %s failed", task_uid)

    finally:
        try:
            reset_dirs(get_tmp_thread_files(task_uid))
        except Exception:
            logger.warning("Cleanup failed for %s", task_uid)
