import os
import subprocess
import requests

image_name = "pysymgym-test"
dockerfile_dir = "../docker"

print(f"Building Docker image '{image_name}'...")
subprocess.run(["docker", "build", "-t", image_name, dockerfile_dir], check=True)
print("Docker build completed.\n")

RESOURCES_DIR = "resources"
os.makedirs(RESOURCES_DIR, exist_ok=True)
DATASET_FILE = os.path.join(RESOURCES_DIR, "dataset.json")


def fetch_dataset():
    url = "https://raw.githubusercontent.com/PySymGym/PySymGym/main/maps/DotNet/Maps/dataset.json"
    print(f"Downloading dataset from {url} ...")
    resp = requests.get(url)
    resp.raise_for_status()

    with open(DATASET_FILE, "wb") as f:
        f.write(resp.content)

    print(f"Dataset saved to {DATASET_FILE}")
    return DATASET_FILE


fetch_dataset()
