"""Тесты для вспомогательных функций screenshot_service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.grpc.screenshot_service import (
    _analysis_to_proto,
    _dt_to_ts,
    _screenshot_to_proto,
    _status_to_proto,
)
from app.grpc.generated import common_pb2
from app.models.db import ScreenshotStatus


# --- _dt_to_ts ---

def test_dt_to_ts_none_returns_zero():
    ts = _dt_to_ts(None)
    assert ts.seconds == 0
    assert ts.nanos == 0


def test_dt_to_ts_aware_datetime():
    dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    ts = _dt_to_ts(dt)
    assert ts.seconds == int(dt.timestamp())


def test_dt_to_ts_naive_treated_as_utc():
    naive = datetime(2024, 6, 1, 12, 0, 0)
    aware = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert _dt_to_ts(naive).seconds == _dt_to_ts(aware).seconds


# --- _status_to_proto ---

@pytest.mark.parametrize("status, expected", [
    (ScreenshotStatus.uploaded,  common_pb2.SCREENSHOT_STATUS_UPLOADED),
    (ScreenshotStatus.analyzing, common_pb2.SCREENSHOT_STATUS_ANALYZING),
    (ScreenshotStatus.completed, common_pb2.SCREENSHOT_STATUS_COMPLETED),
    (ScreenshotStatus.failed,    common_pb2.SCREENSHOT_STATUS_FAILED),
])
def test_status_to_proto(status, expected):
    assert _status_to_proto(status) == expected


# --- _screenshot_to_proto ---

def _make_screenshot(**kwargs) -> SimpleNamespace:
    defaults = dict(
        id=uuid.uuid4(),
        title="My title",
        original_filename="screen.png",
        mime_type="image/png",
        file_size=1024,
        storage_bucket="screenshots",
        storage_key="uploads/abc.png",
        storage_region=None,
        storage_url=None,
        status=ScreenshotStatus.uploaded,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_screenshot_to_proto_basic_fields():
    s = _make_screenshot()
    proto = _screenshot_to_proto(s)

    assert proto.id == str(s.id)
    assert proto.title == "My title"
    assert proto.original_filename == "screen.png"
    assert proto.mime_type == "image/png"
    assert proto.file_size == 1024
    assert proto.storage_bucket == "screenshots"
    assert proto.storage_key == "uploads/abc.png"
    assert proto.status == common_pb2.SCREENSHOT_STATUS_UPLOADED


def test_screenshot_to_proto_nullable_fields_default_to_empty():
    s = _make_screenshot(title=None, storage_region=None, storage_url=None)
    proto = _screenshot_to_proto(s)
    assert proto.title == ""
    assert proto.storage_region == ""
    assert proto.storage_url == ""


# --- _analysis_to_proto ---

def _make_analysis(**kwargs) -> SimpleNamespace:
    defaults = dict(
        id=uuid.uuid4(),
        screenshot_id=uuid.uuid4(),
        model_name="gemma4:31b-cloud",
        summary="Overview",
        error_message=None,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        result_json={
            "screen_type": "dashboard",
            "summary": "A dashboard screen",
            "sections": [{"name": "Header", "description": "Top nav"}],
            "ui_issues": [
                {
                    "title": "Low contrast",
                    "severity": "high",
                    "description": "Text is hard to read",
                    "evidence": "Light grey on white",
                    "recommendation": "Darken text",
                }
            ],
            "ux_suggestions": [{"title": "Add breadcrumb", "description": "Helps navigation"}],
            "implementation_tasks": [
                {"title": "Fix contrast", "description": "Darken body text", "priority": "medium"}
            ],
        },
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_analysis_to_proto_fields():
    a = _make_analysis()
    proto = _analysis_to_proto(a)

    assert proto.id == str(a.id)
    assert proto.screenshot_id == str(a.screenshot_id)
    assert proto.model_name == "gemma4:31b-cloud"
    assert proto.screen_type == "dashboard"
    assert "dashboard" in proto.summary or proto.summary == "Overview"


def test_analysis_to_proto_sections():
    a = _make_analysis()
    proto = _analysis_to_proto(a)
    assert len(proto.sections) == 1
    assert proto.sections[0].name == "Header"
    assert proto.sections[0].description == "Top nav"


def test_analysis_to_proto_ui_issues_severity():
    a = _make_analysis()
    proto = _analysis_to_proto(a)
    assert len(proto.ui_issues) == 1
    assert proto.ui_issues[0].severity == common_pb2.SEVERITY_HIGH
    assert proto.ui_issues[0].title == "Low contrast"


def test_analysis_to_proto_tasks_priority():
    a = _make_analysis()
    proto = _analysis_to_proto(a)
    assert len(proto.implementation_tasks) == 1
    assert proto.implementation_tasks[0].priority == common_pb2.PRIORITY_MEDIUM


def test_analysis_to_proto_empty_result_json():
    a = _make_analysis(result_json=None)
    proto = _analysis_to_proto(a)
    assert len(proto.sections) == 0
    assert len(proto.ui_issues) == 0
