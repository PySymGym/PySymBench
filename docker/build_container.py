import os
import subprocess
import requests
from backend.config.paths import RESOURCES_DIR, DATASET_FILE

IMAGE_NAME = "pysymgym-test"


def fetch_dataset():
    url = "https://raw.githubusercontent.com/PySymGym/PySymGym/main/maps/DotNet/Maps/dataset.json"
    print(f"Downloading dataset from {url} ...")
    resp = requests.get(url)
    resp.raise_for_status()

    with open(DATASET_FILE, "wb") as f:
        f.write(resp.content)

    print(f"Dataset saved to {DATASET_FILE}")
    return DATASET_FILE


def build_container():
    dockerfile_dir = "."

    print(f"Building Docker image '{IMAGE_NAME}'...")
    subprocess.run(["docker", "build", "-t", IMAGE_NAME, dockerfile_dir], check=True)
    print("Docker build completed.\n")

    os.makedirs(RESOURCES_DIR, exist_ok=True)


build_container()
fetch_dataset()
