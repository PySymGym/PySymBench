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
    msg["Subject"] = "Results"
    msg.set_content("Your results are in the attached archive.")

    with open(zip_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=zip_path.name,
        )

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(from_email, from_password)
        server.send_message(msg)

    os.remove(zip_path)
