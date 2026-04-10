import os
import subprocess

from backend.config.paths import (
    DATASET_FILE,
    DOCKER_DIR,
    METHODS_TS_FILE,
    RESOURCES_DIR,
)
from backend.utils.methods_handler import Methods

IMAGE_NAME = "pysymgym-test"


def fetch_dataset(data_upload_file):
    container_name = "temp-fetch-dataset"

    os.makedirs(os.path.dirname(data_upload_file), exist_ok=True)

    try:
        subprocess.run(
            ["docker", "create", "--name", container_name, IMAGE_NAME],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "docker",
                "cp",
                f"{container_name}:/workspace/PySymGym/maps/DotNet/Maps/dataset.json",
                data_upload_file,
            ],
            check=True,
        )

        print(f"Dataset copied to {data_upload_file}")
        return data_upload_file

    finally:
        subprocess.run(["docker", "rm", container_name], capture_output=True)


def build_container():
    print(f"Building Docker image '{IMAGE_NAME}'...")
    subprocess.run(
        ["docker", "build", "--no-cache", "-t", IMAGE_NAME, DOCKER_DIR], check=True
    )
    print("Docker build completed.\n")

    os.makedirs(RESOURCES_DIR, exist_ok=True)


def update_frontend_selection_options(dataset_file, selection_options_file):
    print("Updating frontend selection options...")
    selection_tree = Methods.build_selection_tree_from_dataset(dataset_file)
    Methods.save_selection_to_frontend_file(selection_tree, selection_options_file)


if __name__ == "__main__":
    build_container()
    fetch_dataset(DATASET_FILE)
    update_frontend_selection_options(DATASET_FILE, METHODS_TS_FILE)
