"""Вспомогательные функции для S3-совместимого хранилища (MinIO в локальной разработке)."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

_S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
_S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT", "")  # публичный URL для presigned URL
_S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
_S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
_S3_REGION = os.getenv("S3_REGION", "us-east-1")
_S3_BUCKET = os.getenv("S3_BUCKET", "screenshots")
_PRESIGNED_EXPIRY = int(os.getenv("S3_PRESIGNED_EXPIRY_SECONDS", "900"))  # 15 мин
_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=_S3_ENDPOINT,
        aws_access_key_id=_S3_ACCESS_KEY,
        aws_secret_access_key=_S3_SECRET_KEY,
        region_name=_S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def _get_presign_client():
    """S3-клиент, используемый только для генерации presigned URL.

    Использует публичный endpoint, чтобы сгенерированный URL содержал хост,
    доступный браузеру. Возвращается к внутреннему endpoint, если
    S3_PUBLIC_ENDPOINT не задан.
    """
    endpoint = _S3_PUBLIC_ENDPOINT if _S3_PUBLIC_ENDPOINT else _S3_ENDPOINT
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=_S3_ACCESS_KEY,
        aws_secret_access_key=_S3_SECRET_KEY,
        region_name=_S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket_exists() -> None:
    """Создаёт бакет для скриншотов, если он не существует, и устанавливает политику публичного чтения."""
    import json
    client = _get_s3_client()
    try:
        client.head_bucket(Bucket=_S3_BUCKET)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=_S3_BUCKET)
        else:
            raise

    public_read_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{_S3_BUCKET}/*"],
            }
        ],
    })
    try:
        client.put_bucket_policy(Bucket=_S3_BUCKET, Policy=public_read_policy)
    except ClientError:
        pass


def create_presigned_upload_url(
    filename: str,
    mime_type: str,
    file_size: int,
) -> dict:
    """
    Возвращает presigned PUT URL для прямой загрузки файла из браузера в S3.

    Вызывает ValueError при недопустимом MIME-типе или размере файла.
    Возвращает словарь с ключами: upload_url, bucket, key, expires_at.
    """
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported mime type: {mime_type}")
    if file_size <= 0 or file_size > _MAX_FILE_SIZE:
        raise ValueError(f"File size must be between 1 and {_MAX_FILE_SIZE} bytes")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    key = f"uploads/{uuid.uuid4()}.{ext}"

    client = _get_presign_client()
    upload_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": _S3_BUCKET,
            "Key": key,
            "ContentType": mime_type,
            "ContentLength": file_size,
        },
        ExpiresIn=_PRESIGNED_EXPIRY,
    )

    expires_at = datetime.now(timezone.utc).timestamp() + _PRESIGNED_EXPIRY

    return {
        "upload_url": upload_url,
        "bucket": _S3_BUCKET,
        "key": key,
        "region": _S3_REGION,
        "expires_at": expires_at,
    }


def get_object_bytes(bucket: str, key: str) -> bytes:
    """Скачивает объект из S3 и возвращает его содержимое в виде байтов."""
    client = _get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def delete_s3_object(bucket: str, key: str) -> None:
    """Удаляет объект из S3. Не выбрасывает ошибку, если объект не найден."""
    client = _get_s3_client()
    try:
        client.delete_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code not in ("NoSuchKey", "404"):
            raise
