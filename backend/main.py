from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.docker_runner import run_pipeline
from backend.utils.data_uploader import handle_upload
from backend.utils.methods_handler import Methods
from backend.utils.results_sender import send_folder_by_email
from backend.config.paths import RESULTS_DIR, DATASET_FILE, METHODS_TS_FILE

dataset_methods = Methods(data_filepath=DATASET_FILE, output_filepath=METHODS_TS_FILE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    email: str = Form(...),
    methods: str = Form(...),
    experiment: str = Form(...),
):
    handle_upload(file, methods, dataset_methods)

    run_pipeline()

    send_folder_by_email(
        email,
        RESULTS_DIR,
        experiment,
        file.filename,
    )

    return {
        "experiment": experiment,
        "filename": file.filename,
        "email": email,
        "methods": methods,
        "message": "Data successfully uploaded",
    }
