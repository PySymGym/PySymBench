import os

BASE_DIR = os.getcwd() + "/backend"

RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

DATASET_FILE = os.path.join(RESOURCES_DIR, "dataset.json")
LAUNCH_INFO_FILE = os.path.join(UPLOAD_DIR, "launch_info.csv")
MODEL_ONNX_FILE = os.path.join(UPLOAD_DIR, "model.onnx")
METHODS_TS_FILE = os.path.join(
    BASE_DIR, "../frontend/src/components/components/Methods.ts"
)
