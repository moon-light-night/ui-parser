"""
Юнит-тесты для AnalyzerServicer — stub и ollama пути.

Запуск:
    cd services/analyzer
    python -m pytest tests/test_analyzer_service.py -v
"""
from __future__ import annotations

import json
import sys
import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.analyzer_service import AnalyzerServicer
from app.grpc.generated import analyzer_pb2


# --- Stub-режим ---

class TestBuildStubResponse:
    def setup_method(self):
        self.servicer = AnalyzerServicer()

    def test_returns_success(self):
        resp = self.servicer._build_stub_response("test-id")
        assert resp.success is True

    def test_screen_type_dashboard(self):
        resp = self.servicer._build_stub_response("test-id")
        assert resp.screen_type == "dashboard"

    def test_has_sections(self):
        resp = self.servicer._build_stub_response("test-id")
        assert len(resp.sections) > 0

    def test_has_ui_issues(self):
        resp = self.servicer._build_stub_response("test-id")
        assert len(resp.ui_issues) > 0

    def test_all_ui_issues_have_severity(self):
        resp = self.servicer._build_stub_response("test-id")
        for issue in resp.ui_issues:
            assert issue.severity in ("low", "medium", "high")

    def test_all_tasks_have_priority(self):
        resp = self.servicer._build_stub_response("test-id")
        for task in resp.implementation_tasks:
            assert task.priority in ("low", "medium", "high")

    def test_raw_json_is_valid(self):
        resp = self.servicer._build_stub_response("test-id")
        parsed = json.loads(resp.raw_json)
        assert "screen_type" in parsed

    def test_analysis_id_is_uuid(self):
        resp = self.servicer._build_stub_response("test-id")
        parsed_id = uuid.UUID(resp.analysis_id)  # не выбросит, если валидный UUID
        assert str(parsed_id) == resp.analysis_id


# --- Ollama-режим ---

VALID_OLLAMA_OUTPUT = json.dumps({
    "screen_type": "form",
    "summary": "A login form with email and password fields.",
    "sections": [{"name": "Form body", "description": "Email and password inputs"}],
    "ui_issues": [
        {
            "title": "No error state",
            "severity": "high",
            "description": "Form does not show validation errors",
            "evidence": "Empty field after submit",
            "recommendation": "Add inline error messages",
        }
    ],
    "ux_suggestions": [{"title": "Show password toggle", "description": "Let users reveal password"}],
    "implementation_tasks": [
        {"title": "Add validation", "description": "Validate on blur", "priority": "high"}
    ],
})


class TestAnalyzeWithOllama:
    def setup_method(self):
        self.servicer = AnalyzerServicer()

    @pytest.mark.asyncio
    async def test_no_image_data_returns_failure(self):
        resp = await self.servicer._analyze_with_ollama(
            "sid", "gemma4:31b-cloud", b"", "", None
        )
        assert resp.success is False
        assert "required" in resp.error_message.lower()

    @pytest.mark.asyncio
    async def test_ollama_success_parses_response(self):
        mock_response = {"message": {"content": VALID_OLLAMA_OUTPUT}}

        with patch("app.analyzer_service.chat_completion", new=AsyncMock(return_value=mock_response)):
            resp = await self.servicer._analyze_with_ollama(
                "sid", "gemma4:31b-cloud", b"fake-image-bytes", "", None
            )

        assert resp.success is True
        assert resp.screen_type == "form"
        assert len(resp.sections) == 1
        assert resp.sections[0].name == "Form body"
        assert len(resp.ui_issues) == 1
        assert resp.ui_issues[0].severity == "high"
        assert len(resp.implementation_tasks) == 1
        assert resp.implementation_tasks[0].priority == "high"

    @pytest.mark.asyncio
    async def test_ollama_exception_returns_failure(self):
        with patch(
            "app.analyzer_service.chat_completion",
            new=AsyncMock(side_effect=Exception("connection refused")),
        ):
            resp = await self.servicer._analyze_with_ollama(
                "sid", "gemma4:31b-cloud", b"fake-image-bytes", "", None
            )

        assert resp.success is False
        assert "Ollama request failed" in resp.error_message

    @pytest.mark.asyncio
    async def test_ollama_invalid_json_falls_back_gracefully(self):
        bad_response = {"message": {"content": "Sorry, I cannot analyze this."}}

        with patch("app.analyzer_service.chat_completion", new=AsyncMock(return_value=bad_response)):
            resp = await self.servicer._analyze_with_ollama(
                "sid", "gemma4:31b-cloud", b"fake-image-bytes", "", None
            )

        # Парсер должен вернуть fallback, сервис — успешный ответ с screen_type=unknown
        assert resp.success is True
        assert resp.screen_type == "unknown"
