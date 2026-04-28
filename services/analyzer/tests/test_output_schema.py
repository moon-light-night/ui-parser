"""
Юнит-тесты для output_schema.parse_analysis_output.

Запуск:
    cd services/analyzer
    pip install pytest pydantic
    python -m pytest tests/ -v
"""
from __future__ import annotations

import json
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.output_schema import parse_analysis_output, AnalysisOutput


# Вспомогательные данные

VALID_JSON = {
    "screen_type": "dashboard",
    "summary": "A data-heavy analytics dashboard.",
    "sections": [
        {"name": "Header", "description": "Top navigation bar"},
        {"name": "Charts", "description": "Main data visualisation area"},
    ],
    "ui_issues": [
        {
            "title": "Low contrast text",
            "severity": "high",
            "description": "Secondary labels fail WCAG AA.",
            "evidence": "Gray-400 on white background",
            "recommendation": "Darken to Gray-600.",
        }
    ],
    "ux_suggestions": [
        {"title": "Add keyboard shortcuts", "description": "Power users expect shortcuts."}
    ],
    "implementation_tasks": [
        {"title": "Fix contrast", "description": "Update color tokens.", "priority": "high"}
    ],
}


# Тесты штатного поведения

class TestParseAnalysisOutputHappyPath:
    def test_clean_json_string(self):
        raw = json.dumps(VALID_JSON)
        result = parse_analysis_output(raw)
        assert isinstance(result, AnalysisOutput)
        assert result.screen_type == "dashboard"
        assert result.summary == "A data-heavy analytics dashboard."
        assert len(result.sections) == 2
        assert result.sections[0].name == "Header"

    def test_markdown_fence_stripped(self):
        raw = f"```json\n{json.dumps(VALID_JSON)}\n```"
        result = parse_analysis_output(raw)
        assert result.screen_type == "dashboard"

    def test_markdown_fence_without_language(self):
        raw = f"```\n{json.dumps(VALID_JSON)}\n```"
        result = parse_analysis_output(raw)
        assert result.screen_type == "dashboard"

    def test_leading_prose_then_json(self):
        prose = "Here is my analysis:\n"
        raw = prose + json.dumps(VALID_JSON)
        result = parse_analysis_output(raw)
        assert result.screen_type == "dashboard"

    def test_ui_issues_severity_normalised_lowercase(self):
        data = {**VALID_JSON, "ui_issues": [
            {"title": "A", "severity": "HIGH", "description": "d", "evidence": "e", "recommendation": "r"},
        ]}
        result = parse_analysis_output(json.dumps(data))
        assert result.ui_issues[0].severity == "high"

    def test_implementation_tasks_priority_normalised(self):
        data = {**VALID_JSON, "implementation_tasks": [
            {"title": "T", "description": "d", "priority": "MEDIUM"},
        ]}
        result = parse_analysis_output(json.dumps(data))
        assert result.implementation_tasks[0].priority == "medium"

    def test_screen_type_normalised(self):
        # Validator lowercases the value if it's in the allowed set
        data = {**VALID_JSON, "screen_type": "LANDING_PAGE"}
        result = parse_analysis_output(json.dumps(data))
        assert result.screen_type == "landing_page"

    def test_screen_type_landing_page_lowercase(self):
        data = {**VALID_JSON, "screen_type": "landing_page"}
        result = parse_analysis_output(json.dumps(data))
        assert result.screen_type == "landing_page"

    def test_all_known_screen_types_accepted(self):
        known = ["landing_page", "dashboard", "form", "settings", "modal", "mobile_screen", "unknown"]
        for st in known:
            data = {**VALID_JSON, "screen_type": st}
            result = parse_analysis_output(json.dumps(data))
            assert result.screen_type == st, f"screen_type={st!r} should be accepted"

    def test_empty_lists_allowed(self):
        data = {**VALID_JSON, "sections": [], "ui_issues": [], "ux_suggestions": [], "implementation_tasks": []}
        result = parse_analysis_output(json.dumps(data))
        assert result.sections == []
        assert result.ui_issues == []


# Тесты отказоустойчивости

class TestParseAnalysisOutputFaultTolerance:
    def test_invalid_json_returns_fallback(self):
        result = parse_analysis_output("this is definitely not JSON")
        assert isinstance(result, AnalysisOutput)
        assert result.screen_type == "unknown"
        assert "this is definitely not JSON" in result.summary

    def test_empty_string_returns_fallback(self):
        result = parse_analysis_output("")
        assert isinstance(result, AnalysisOutput)
        assert result.screen_type == "unknown"

    def test_partial_json_missing_required_fields(self):
        # Присутствует только summary, остальные поля отсутствуют
        raw = json.dumps({"summary": "Just a summary"})
        result = parse_analysis_output(raw)
        assert result.summary == "Just a summary"
        assert result.screen_type == "unknown"
        assert result.sections == []

    def test_unknown_screen_type_falls_back_to_unknown(self):
        data = {**VALID_JSON, "screen_type": "wizard"}
        result = parse_analysis_output(json.dumps(data))
        assert result.screen_type == "unknown"

    def test_invalid_severity_defaults_to_medium(self):
        data = {**VALID_JSON, "ui_issues": [
            {"title": "X", "severity": "critical", "description": "d", "evidence": "e", "recommendation": "r"}
        ]}
        result = parse_analysis_output(json.dumps(data))
        assert result.ui_issues[0].severity == "medium"

    def test_invalid_priority_defaults_to_medium(self):
        data = {**VALID_JSON, "implementation_tasks": [
            {"title": "X", "description": "d", "priority": "urgent"}
        ]}
        result = parse_analysis_output(json.dumps(data))
        assert result.implementation_tasks[0].priority == "medium"

    def test_extra_unknown_fields_ignored(self):
        data = {**VALID_JSON, "unknown_key": "should be ignored", "another": 42}
        result = parse_analysis_output(json.dumps(data))
        assert result.screen_type == "dashboard"

    def test_raw_text_truncated_in_fallback_summary(self):
        long_text = "x" * 1000
        result = parse_analysis_output(long_text)
        assert len(result.summary) <= 500
