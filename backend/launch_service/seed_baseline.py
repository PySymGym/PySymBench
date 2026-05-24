import csv as csv_module
import logging
import os
import shutil

import shortuuid

from backend.config.paths import (
    CPP_LAUNCH_INFO_FILE,
    CSHARP_LAUNCH_INFO_FILE,
    JAVA_LAUNCH_INFO_FILE,
    LAUNCH_INFO_FILE,
    RESULTS_DIR,
    UPLOAD_DIR,
    get_thread_filepath,
    get_tmp_thread_files,
)
from backend.db.repository import save_experiment
from backend.file_utils.files import reset_dirs
from backend.file_utils.runstrat_metrics import (
    RunstratMetrics,
    combine_metrics,
    compute_metrics,
    merge_csvs,
)
from backend.storage.minio_client import upload_file
from backend.utils.docker_runner import RunstratBaseline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LANGUAGE_CSVS: dict[str, str] = {
    "csharp": CSHARP_LAUNCH_INFO_FILE,
    "java": JAVA_LAUNCH_INFO_FILE,
    "cpp": CPP_LAUNCH_INFO_FILE,
}


def _baseline_csv_path(uid: str, lang: str) -> str:
    return os.path.join(
        get_thread_filepath(uid, RESULTS_DIR),
        f"artifacts_run_baseline_{lang}",
        "ExecutionTreeContributedCoverage.csv",
    )


def _count_methods_in_csv(csv_path: str) -> int:
    with open(csv_path, newline="") as f:
        reader = csv_module.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def seed_baseline():
    uid = str(shortuuid.uuid())
    logger.info("Seeding baseline with uid=%s", uid)

    os.makedirs(get_thread_filepath(uid, UPLOAD_DIR), exist_ok=True)
    os.makedirs(get_thread_filepath(uid, RESULTS_DIR), exist_ok=True)

    metrics_by_lang: dict[str, RunstratMetrics] = {}

    try:
        for lang, csv_src in LANGUAGE_CSVS.items():
            try:
                methods_launched = _count_methods_in_csv(csv_src)
                if methods_launched == 0:
                    logger.info("Skipping %s — launch CSV is empty", lang)
                    continue

                shutil.copy(csv_src, get_thread_filepath(uid, LAUNCH_INFO_FILE))
                RunstratBaseline(out_suffix=f"_{lang}").run(uid)

                baseline_csv = _baseline_csv_path(uid, lang)
                metrics = compute_metrics(baseline_csv)
                metrics_by_lang[lang] = metrics

                results_object_key = None
                try:
                    results_object_key = upload_file(
                        baseline_csv,
                        f"baseline/{lang}/ExecutionTreeContributedCoverage.csv",
                    )
                except Exception:
                    logger.exception("MinIO upload failed for language %s", lang)

                record_id = save_experiment(
                    experiment_name="Baseline",
                    model_name="ExecutionTreeContributedCoverage",
                    email="",
                    metrics=metrics,
                    methods_launched=methods_launched,
                    language=lang,
                    is_baseline=True,
                    results_object_key=results_object_key,
                )
                logger.info(
                    "Saved %s baseline id=%d  mean=%.4f  tests=%d  errors=%d  time=%.2fs",
                    lang,
                    record_id,
                    metrics.mean_coverage,
                    metrics.total_tests,
                    metrics.total_errors,
                    metrics.total_time_sec,
                )
            except Exception:
                logger.exception("Baseline failed for language %s", lang)

        if len(metrics_by_lang) >= 1:
            all_csvs = [_baseline_csv_path(uid, lang) for lang in metrics_by_lang]
            combined = combine_metrics(all_csvs)
            total_launched = sum(
                _count_methods_in_csv(LANGUAGE_CSVS[lang]) for lang in metrics_by_lang
            )

            merged_csv_path = os.path.join(
                get_thread_filepath(uid, RESULTS_DIR), "baseline_all.csv"
            )
            merge_csvs(all_csvs, merged_csv_path)

            all_results_key = None
            try:
                all_results_key = upload_file(
                    merged_csv_path, "baseline/all/ExecutionTreeContributedCoverage.csv"
                )
            except Exception:
                logger.exception("MinIO upload failed for all baseline")

            record_id = save_experiment(
                experiment_name="Baseline",
                model_name="ExecutionTreeContributedCoverage",
                email="",
                metrics=combined,
                methods_launched=total_launched,
                language="all",
                is_baseline=True,
                results_object_key=all_results_key,
            )
            logger.info(
                "Saved aggregated baseline id=%d  mean=%.4f  tests=%d  errors=%d  time=%.2fs",
                record_id,
                combined.mean_coverage,
                combined.total_tests,
                combined.total_errors,
                combined.total_time_sec,
            )
    finally:
        reset_dirs(get_tmp_thread_files(uid))


if __name__ == "__main__":
    seed_baseline()
