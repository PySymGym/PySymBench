from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import json, csv, shutil
from dotenv import load_dotenv

from run_compstrat import run_compstrat
from run_runstrat import run_runstrat, run_runstrat_ai
from methods.methods import Methods
from send_results import send_folder_by_email

load_dotenv()

RESOURCES_DIR = "resources"
os.makedirs(RESOURCES_DIR, exist_ok=True)
DATASET_FILE = os.path.join(RESOURCES_DIR, "dataset.json")

frontend_methods_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
    "src",
    "components",
    "components",
    "Methods.ts"
)

dataset_methods = Methods(data_filepath=DATASET_FILE,
                          output_filepath=frontend_methods_path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

METHODS_FILE = os.path.join(UPLOAD_DIR, "launch_info.csv")
RESULTS_DIR = os.path.join("results")

if not os.path.exists(METHODS_FILE):
    with open(METHODS_FILE, "w") as f:
        json.dump([], f)


@app.post("/api/upload")
async def upload_file(
        file: UploadFile = File(...),
        email: str = Form(...),
        methods: str = Form(...),
        experiment: str = Form(...),
):
    try:
        methods_list = json.loads(methods)
        if not isinstance(methods_list, list):
            methods_list = []
    except Exception:
        methods_list = []

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        while content := file.file.read(1024 * 1024):
            f.write(content)

    with open(METHODS_FILE, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["dll", "method"])

        sel_methods = dataset_methods.get_methods_list(methods_list)
        for item in sel_methods:
            if "," in item:
                dll, method = item.split(",", 1)
                writer.writerow([dll, method])

    folder_path = "results"

    shutil.rmtree(folder_path)
    os.makedirs(folder_path)

    run_runstrat()
    run_runstrat_ai()
    run_compstrat()
    send_folder_by_email(email, RESULTS_DIR, os.getenv("EMAIL"), os.getenv("APP_PASSWORD"), experiment, file.filename)

    return {
        "filename": file.filename,
        "email": email,
        "methods": methods_list,
        "message": "Data successfully uploaded"
    }
