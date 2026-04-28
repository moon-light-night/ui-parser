"""Тесты для вспомогательных функций chat_service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.grpc.chat_service import (
    _dt_to_ts,
    _error_event,
    _message_to_proto,
    _session_to_proto,
)
from app.grpc.generated import common_pb2
from app.models.db import MessageRole, MessageStatus


# --- _session_to_proto ---

def _make_session(**kwargs) -> SimpleNamespace:
    defaults = dict(
        id=uuid.uuid4(),
        screenshot_id=uuid.uuid4(),
        title="My session",
        created_at=datetime(2024, 3, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 3, 2, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_session_to_proto_fields():
    session = _make_session()
    proto = _session_to_proto(session, message_count=5)

    assert proto.id == str(session.id)
    assert proto.screenshot_id == str(session.screenshot_id)
    assert proto.title == "My session"
    assert proto.message_count == 5


def test_session_to_proto_default_message_count():
    session = _make_session()
    proto = _session_to_proto(session)
    assert proto.message_count == 0


# --- _message_to_proto ---

def _make_message(**kwargs) -> SimpleNamespace:
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role=MessageRole.user,
        content="Hello",
        status=MessageStatus.completed,
        model_name=None,
        created_at=datetime(2024, 3, 1, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_message_to_proto_user_role():
    msg = _make_message(role=MessageRole.user)
    proto = _message_to_proto(msg)
    assert proto.role == common_pb2.MESSAGE_ROLE_USER


def test_message_to_proto_assistant_role():
    msg = _make_message(role=MessageRole.assistant)
    proto = _message_to_proto(msg)
    assert proto.role == common_pb2.MESSAGE_ROLE_ASSISTANT


def test_message_to_proto_status_streaming():
    msg = _make_message(status=MessageStatus.streaming)
    proto = _message_to_proto(msg)
    assert proto.status == common_pb2.MESSAGE_STATUS_STREAMING


def test_message_to_proto_model_name_none_returns_empty():
    msg = _make_message(model_name=None)
    proto = _message_to_proto(msg)
    assert proto.model_name == ""


def test_message_to_proto_content():
    msg = _make_message(content="What is this screen?")
    proto = _message_to_proto(msg)
    assert proto.content == "What is this screen?"


# --- _error_event ---

def test_error_event_fields():
    event = _error_event("NOT_FOUND", "session not found")
    assert event.error.code == "NOT_FOUND"
    assert event.error.message == "session not found"


# --- _dt_to_ts (chat_service version) ---

def test_dt_to_ts_utc():
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts = _dt_to_ts(dt)
    assert ts.seconds == int(dt.timestamp())
    assert ts.nanos >= 0


def test_dt_to_ts_none():
    ts = _dt_to_ts(None)
    assert ts.seconds == 0
