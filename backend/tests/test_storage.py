"""Тесты для app/storage.py — валидация входных данных create_presigned_upload_url."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.storage import create_presigned_upload_url, ALLOWED_MIME_TYPES


# --- Валидация mime_type ---

def test_invalid_mime_type_raises():
    with pytest.raises(ValueError, match="Unsupported mime type"):
        create_presigned_upload_url("file.pdf", "application/pdf", 1024)


def test_unsupported_mime_type_not_in_allowed():
    assert "application/pdf" not in ALLOWED_MIME_TYPES


# --- Валидация file_size ---

def test_zero_file_size_raises():
    with pytest.raises(ValueError, match="File size must be"):
        create_presigned_upload_url("file.png", "image/png", 0)


def test_negative_file_size_raises():
    with pytest.raises(ValueError, match="File size must be"):
        create_presigned_upload_url("file.png", "image/png", -1)


def test_exceeding_file_size_raises():
    too_large = 20 * 1024 * 1024 + 1
    with pytest.raises(ValueError, match="File size must be"):
        create_presigned_upload_url("file.png", "image/png", too_large)


# --- Успешный путь (мокаем boto3) ---

def test_valid_input_returns_expected_keys():
    fake_url = "https://minio.local/presigned"
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = fake_url

    with patch("app.storage._get_presign_client", return_value=mock_client):
        result = create_presigned_upload_url("screen.png", "image/png", 512)

    assert result["upload_url"] == fake_url
    assert result["bucket"] is not None
    assert result["key"].startswith("uploads/")
    assert result["key"].endswith(".png")
    assert result["expires_at"] > 0


def test_key_contains_uuid_and_extension():
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://minio.local/url"

    with patch("app.storage._get_presign_client", return_value=mock_client):
        result = create_presigned_upload_url("photo.jpeg", "image/jpeg", 2048)

    key = result["key"]
    # uploads/<uuid>.jpeg
    parts = key.split("/")
    assert parts[0] == "uploads"
    assert parts[1].endswith(".jpeg")
