"""Вспомогательные функции для работы с S3-совместимым хранилищем в сервисе анализатора."""
from __future__ import annotations

import os

import boto3
from botocore.client import Config

_S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
_S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
_S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
_S3_REGION = os.getenv("S3_REGION", "us-east-1")


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=_S3_ENDPOINT,
        aws_access_key_id=_S3_ACCESS_KEY,
        aws_secret_access_key=_S3_SECRET_KEY,
        region_name=_S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def get_object_bytes(bucket: str, key: str) -> bytes:
    """Скачивает объект из S3-совместимого хранилища и возвращает сырые байты."""
    client = _get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()
