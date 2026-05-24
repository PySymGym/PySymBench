import logging
import os
from pathlib import Path

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


def _get_client() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "")
    secret_key = os.getenv("MINIO_SECRET_KEY", "")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def _ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        logger.info("Created MinIO bucket: %s", bucket)


def upload_file(local_path: str | Path, object_key: str) -> str:
    bucket = os.getenv("MINIO_BUCKET", "pysymbench")
    client = _get_client()
    _ensure_bucket(client, bucket)
    client.fput_object(bucket, object_key, str(local_path))
    logger.info("Uploaded %s → minio://%s/%s", local_path, bucket, object_key)
    return object_key


def stream_object(object_key: str):
    bucket = os.getenv("MINIO_BUCKET", "pysymbench")
    client = _get_client()
    return client.get_object(bucket, object_key)


def download_file(object_key: str, local_path: str | Path) -> None:
    bucket = os.getenv("MINIO_BUCKET", "pysymbench")
    client = _get_client()
    os.makedirs(os.path.dirname(str(local_path)), exist_ok=True)
    client.fget_object(bucket, object_key, str(local_path))
    logger.info("Downloaded minio://%s/%s → %s", bucket, object_key, local_path)


def get_presigned_url(object_key: str, expires_hours: int = 24) -> str:
    from datetime import timedelta

    bucket = os.getenv("MINIO_BUCKET", "pysymbench")
    client = _get_client()
    try:
        url = client.presigned_get_object(
            bucket, object_key, expires=timedelta(hours=expires_hours)
        )
        return url
    except S3Error:
        logger.exception("Failed to generate presigned URL for %s", object_key)
        raise
