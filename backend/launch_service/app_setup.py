import os
import subprocess
import requests
from backend.config.paths import (
    RESOURCES_DIR,
    DATASET_FILE,
    DOCKER_DIR,
    METHODS_TS_FILE,
)
from backend.utils.methods_handler import Methods

IMAGE_NAME = "pysymgym-test"
URL = "https://raw.githubusercontent.com/PySymGym/PySymGym/main/maps/DotNet/Maps/dataset.json"


def fetch_dataset(url, data_upload_file):
    print(f"Downloading dataset from {url} ...")
    resp = requests.get(url)
    resp.raise_for_status()

    with open(data_upload_file, "wb") as f:
        f.write(resp.content)

    print(f"Dataset saved to {data_upload_file}")
    return data_upload_file


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
    fetch_dataset(URL, DATASET_FILE)
    update_frontend_selection_options(DATASET_FILE, METHODS_TS_FILE)
