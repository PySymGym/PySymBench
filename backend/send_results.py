import os
import zipfile
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def send_folder_by_email(
        to_email: str,
        folder_path: str,
        from_email: str,
        from_password: str,
        experiment_name: str,
        model_name: str,
):
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder not found: {folder_path}")

    zip_path = folder.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder.rglob("*"):
            zipf.write(file, file.relative_to(folder))

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = f"Results of {experiment_name} with {model_name[:-5]}"

    message = (
        f"\n\n"
        f"The results of the experiment '{experiment_name}' using the model '{model_name[:-5]}' are ready. "
        f"Please find the details in the attached ZIP file.\n\n"
        f"Contents of the ZIP:\n"
        f" - Model run results: artifact_run_ai folder\n"
        f" - Baseline run results: artifact_run_baseline folder\n"
        f" - Comparison with baseline: compstrat_results folder\n\n"
    )

    msg.set_content(message)

    with open(zip_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=zip_path.name,
        )

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(from_email, from_password)
            server.send_message(msg)
    finally:
        if zip_path.exists():
            os.remove(zip_path)
