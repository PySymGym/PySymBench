import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def get_tmp_thread_files(uid):
    return [get_thread_filepath(uid, UPLOAD_DIR), get_thread_filepath(uid, RESULTS_DIR)]


def get_thread_filepath(uid, filepath):
    base_prefix = TMP_FILE_DIR + os.sep
    new_prefix = f"{TMP_FILE_DIR}/{uid}"
    return filepath.replace(base_prefix, new_prefix)


DOCKER_DIR = os.path.join(os.getcwd(), "docker")
BASE_DIR = os.path.join(os.getcwd(), "backend")
TMP_FILE_DIR = os.path.join(BASE_DIR, "tmp")

RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
UPLOAD_DIR = os.path.join(TMP_FILE_DIR, "uploads")
RESULTS_DIR = os.path.join(TMP_FILE_DIR, "results")

DATASET_FILE = os.path.join(RESOURCES_DIR, "dataset.json")
CSHARP_LAUNCH_INFO_FILE = os.path.join(RESOURCES_DIR, "csharp_launch_info.csv")
JAVA_LAUNCH_INFO_FILE = os.path.join(RESOURCES_DIR, "java_launch_info.csv")
CPP_LAUNCH_INFO_FILE = os.path.join(RESOURCES_DIR, "cpp_launch_info.csv")
LAUNCH_INFO_FILE = os.path.join(UPLOAD_DIR, "launch_info.csv")
MODEL_ONNX_FILE = os.path.join(UPLOAD_DIR, "model.onnx")
METHODS_TS_FILE = os.path.join(
    BASE_DIR, "../frontend/src/components/components/Methods.ts"
)
COMPSTRAT_RESULTS_DIR = os.path.join(RESULTS_DIR, "compstrat_results")
ARTIFACTS_AI_CSV_FILE = os.path.join(RESULTS_DIR, "artifacts_run_ai/AI.csv")
ARTIFACTS_AI2_CSV_FILE = os.path.join(RESULTS_DIR, "artifacts_run_ai2/AI.csv")
ARTIFACTS_BASELINE_CSV_FILE = os.path.join(
    RESULTS_DIR, "artifacts_run_baseline/ExecutionTreeContributedCoverage.csv"
)
MODEL2_ONNX_FILE = os.path.join(UPLOAD_DIR, "model2.onnx")
COMPARISON_STRAT1_CSV = os.path.join(RESULTS_DIR, "strat1/AI.csv")
COMPARISON_STRAT2_CSV = os.path.join(RESULTS_DIR, "strat2/AI.csv")
