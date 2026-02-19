from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from backend.methods_parser import methods_parser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

EMAIL_FILE = os.path.join(UPLOAD_DIR, "emails.txt")
METHODS_FILE = os.path.join(UPLOAD_DIR, "methods.json")

if not os.path.exists(METHODS_FILE):
    with open(METHODS_FILE, "w") as f:
        json.dump([], f)


@app.post("/api/upload")
async def upload_file(
        file: UploadFile = File(...),
        email: str = Form(...),
        methods: str = Form(...)
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

    with open(EMAIL_FILE, "a") as f:
        f.write(email + "\n")

    with open(METHODS_FILE, "r+") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
        except Exception:
            data = []
        methods = methods_parser(methods_list)
        data.append(methods)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    return {
        "filename": file.filename,
        "email": email,
        "methods": methods_list,
        "message": "Data successfully uploaded"
    }
