import logging
import os
import smtplib
import ssl
import zipfile
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

from backend.file_utils.runstrat_metrics import RunstratMetrics

logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 15


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set")
    return value


def send_folder_by_email(
    to_email: str,
    folder_path: str,
    experiment_name: str,
    model_file_name: str,
    comparison_mode: str = "baseline",
    model2_file_name: str | None = None,
):
    load_dotenv()

    from_email = require_env("EMAIL")
    from_password = require_env("APP_PASSWORD")

    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"Folder not found: {folder_path}")

    zip_path = folder.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder.rglob("*"):
            zipf.write(file, file.relative_to(folder))

    model_name = (
        model_file_name[:-5] if model_file_name.endswith(".onnx") else model_file_name
    )

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email

    if comparison_mode == "model" and model2_file_name:
        model2_name = (
            model2_file_name[:-5]
            if model2_file_name.endswith(".onnx")
            else model2_file_name
        )
        msg["Subject"] = f"Results of {experiment_name}: {model_name} vs {model2_name}"
        message = (
            f"\n\n"
            f"The results of the experiment '{experiment_name}' comparing "
            f"'{model_name}' against '{model2_name}' are ready.\n\n"
            f"Contents of the ZIP:\n"
            f" - Model 1 run results: artifacts_run_ai folder\n"
            f" - Model 2 run results: artifacts_run_ai2 folder\n"
            f" - Comparison between models: compstrat_results folder\n\n"
        )
    else:
        msg["Subject"] = f"Results of {experiment_name} with {model_name}"
        message = (
            f"\n\n"
            f"The results of the experiment '{experiment_name}' "
            f"using the model '{model_name}' are ready.\n\n"
            f"Contents of the ZIP:\n"
            f" - Model run results: artifacts_run_ai folder\n"
            f" - Baseline run results: artifacts_run_baseline folder\n"
            f" - Comparison with baseline: compstrat_results folder\n\n"
        )

    msg.set_content(message)

    with open(zip_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename="results.zip",
        )

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=SMTP_TIMEOUT,
        ) as server:
            server.ehlo()

            server.starttls(context=context)

            server.ehlo()

            server.login(from_email, from_password)

            server.send_message(msg)

    except (smtplib.SMTPException, TimeoutError, OSError):
        logger.exception("Email sending failed")
        raise

    finally:
        if zip_path.exists():
            os.remove(zip_path)


def send_task_started_email(
    to_email: str,
    experiment_name: str,
    model_file_name: str,
    cancel_url: str,
):
    load_dotenv()

    from_email = require_env("EMAIL")
    from_password = require_env("APP_PASSWORD")

    model_name = (
        model_file_name[:-5] if model_file_name.endswith(".onnx") else model_file_name
    )

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = f"Experiment '{experiment_name}' has started"

    body = (
        f"\n\n"
        f"Your experiment '{experiment_name}' using model '{model_name}' "
        f"has been submitted and is now running.\n\n"
        f"If you want to cancel it, open the link below:\n"
        f"{cancel_url}\n\n"
        f"The link expires in 24 hours.\n"
    )

    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(from_email, from_password)
            server.send_message(msg)
    except (smtplib.SMTPException, TimeoutError, OSError):
        logger.exception("Email sending failed")
        raise


def send_publish_results_by_email(
    to_email: str,
    metrics: RunstratMetrics,
    experiment_name: str,
    model_file_name: str,
):
    load_dotenv()

    from_email = require_env("EMAIL")
    from_password = require_env("APP_PASSWORD")

    model_name = model_file_name[:-5]

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = f"Results of {experiment_name} with {model_name}"

    body = (
        f"\n\n"
        f"The symbolic execution results for experiment '{experiment_name}' "
        f"using the model '{model_name}' have been "
        f"successfully processed and published to the ranking.\n\n"
        f"Metrics:\n"
        f"  Total tests:      {metrics.total_tests}\n"
        f"  Total errors:     {metrics.total_errors}\n"
        f"  Mean coverage:    {metrics.mean_coverage:.4f}\n"
        f"  Median coverage:  {metrics.median_coverage:.4f}\n"
        f"  Total time (sec): {metrics.total_time_sec:.2f}\n"
    )

    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=SMTP_TIMEOUT,
        ) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(from_email, from_password)
            server.send_message(msg)

    except (smtplib.SMTPException, TimeoutError, OSError):
        logger.exception("Email sending failed")
        raise
