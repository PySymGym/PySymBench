import logging
import os
import shutil

import shortuuid

from backend.config.paths import (
    ARTIFACTS_BASELINE_CSV_FILE,
    LAUNCH_INFO_FILE,
    RANKING_LAUNCH_INFO_FILE,
    RESULTS_DIR,
    UPLOAD_DIR,
    get_thread_filepath,
    get_tmp_thread_files,
)
from backend.db.repository import save_experiment
from backend.file_utils.files import reset_dirs
from backend.file_utils.runstrat_metrics import compute_metrics
from backend.utils.docker_runner import RunstratBaseline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def seed_baseline():
    uid = str(shortuuid.uuid())
    logger.info("Seeding baseline with uid=%s", uid)

    os.makedirs(get_thread_filepath(uid, UPLOAD_DIR), exist_ok=True)
    os.makedirs(get_thread_filepath(uid, RESULTS_DIR), exist_ok=True)

    shutil.copy(RANKING_LAUNCH_INFO_FILE, get_thread_filepath(uid, LAUNCH_INFO_FILE))

    try:
        RunstratBaseline().run(uid)

        baseline_csv = get_thread_filepath(uid, ARTIFACTS_BASELINE_CSV_FILE)
        metrics = compute_metrics(baseline_csv)

        record_id = save_experiment(
            experiment_name="Baseline",
            model_name="ExecutionTreeContributedCoverage",
            email="",
            metrics=metrics,
            is_baseline=True,
        )
        logger.info("Saved baseline as experiment id=%d", record_id)
        logger.info(
            "mean_coverage=%.4f  median_coverage=%.4f  total_tests=%d  "
            "total_errors=%d  time=%.2fs",
            metrics.mean_coverage,
            metrics.median_coverage,
            metrics.total_tests,
            metrics.total_errors,
            metrics.total_time_sec,
        )
    finally:
        reset_dirs(get_tmp_thread_files(uid))


if __name__ == "__main__":
    seed_baseline()
