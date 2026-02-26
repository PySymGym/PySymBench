from celery import Celery
from backend.utils.docker_runner import run_pipeline
from backend.utils.results_sender import send_folder_by_email
from backend.config.paths import RESULTS_DIR, get_thread_filepath, get_tmp_thread_files
from backend.file_utils.files import reset_dirs

celery_app = Celery(
    "tasks", broker="redis://localhost:6379", backend="redis://localhost:6379"
)


@celery_app.task
def process_and_cleanup_task(task_uid: str, email: str, experiment: str, filename: str):
    run_pipeline(task_uid)

    send_folder_by_email(
        email,
        get_thread_filepath(task_uid, RESULTS_DIR),
        experiment,
        filename,
    )

    tmp_thread_dirs = get_tmp_thread_files(task_uid)
    reset_dirs(tmp_thread_dirs)
