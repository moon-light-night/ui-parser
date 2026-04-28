"""
Юнит-тесты для prompts.py — build_chat_system_prompt и build_chat_messages.

Запуск:
    cd services/analyzer
    python -m pytest tests/test_prompts.py -v
"""
from __future__ import annotations

import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.prompts import build_chat_system_prompt, build_chat_messages, ANALYSIS_SYSTEM_PROMPT


class TestAnalysisSystemPrompt:
    def test_contains_json_schema_keys(self):
        assert "screen_type" in ANALYSIS_SYSTEM_PROMPT
        assert "ui_issues" in ANALYSIS_SYSTEM_PROMPT
        assert "severity" in ANALYSIS_SYSTEM_PROMPT
        assert "implementation_tasks" in ANALYSIS_SYSTEM_PROMPT
        assert "priority" in ANALYSIS_SYSTEM_PROMPT

    def test_demands_json_only_output(self):
        # Промпт должен инструктировать модель возвращать только JSON
        lower = ANALYSIS_SYSTEM_PROMPT.lower()
        assert "json" in lower
        assert "only" in lower or "no" in lower


class TestBuildChatSystemPrompt:
    def _analysis_json(self):
        return json.dumps({
            "sections": [{"name": "Header", "description": "Nav"}],
            "ui_issues": [{"title": "Low contrast", "severity": "high",
                           "description": "Fails WCAG", "evidence": "e", "recommendation": "r"}],
            "ux_suggestions": [{"title": "Add shortcuts", "description": "d"}],
            "implementation_tasks": [{"title": "Fix contrast", "description": "d", "priority": "high"}],
        })

    def test_contains_filename(self):
        prompt = build_chat_system_prompt(
            original_filename="dashboard.png",
            screen_type="dashboard",
            summary="A KPI dashboard",
            analysis_json="",
        )
        assert "dashboard.png" in prompt

    def test_contains_screen_type(self):
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="form",
            summary="A login form",
            analysis_json="",
        )
        assert "form" in prompt

    def test_contains_summary(self):
        summary = "A data-heavy analytics dashboard with sidebar"
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="dashboard",
            summary=summary,
            analysis_json="",
        )
        assert summary in prompt

    def test_analysis_context_includes_issues(self):
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="dashboard",
            summary="Summary",
            analysis_json=self._analysis_json(),
        )
        assert "Low contrast" in prompt
        assert "Header" in prompt
        assert "Add shortcuts" in prompt
        assert "Fix contrast" in prompt

    def test_no_analysis_shows_fallback_note(self):
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="",
            summary="",
            analysis_json="",
        )
        # Промпт на русском — проверяем ключевое слово об отсутствии анализа
        assert "Анализ" in prompt or "анализ" in prompt

    def test_grounding_instructions_present(self):
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="dashboard",
            summary="Dashboard",
            analysis_json=self._analysis_json(),
        )
        lower = prompt.lower()
        # Промпт на русском — проверяем инструкции об обоснованности и неуверенности
        assert "уверен" in lower or "неуверен" in lower or "не уверен" in lower
        assert "скриншот" in lower or "анализ" in lower

    def test_malformed_analysis_json_does_not_crash(self):
        prompt = build_chat_system_prompt(
            original_filename="ui.png",
            screen_type="dashboard",
            summary="Dashboard",
            analysis_json="{not valid json}",
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestBuildChatMessages:
    def test_system_prompt_is_first(self):
        messages = build_chat_messages(
            system_prompt="You are a helpful assistant.",
            history=[],
            user_message="Hello",
        )
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant."

    def test_user_message_is_last(self):
        messages = build_chat_messages(
            system_prompt="System.",
            history=[{"role": "user", "content": "Previous"}, {"role": "assistant", "content": "Answer"}],
            user_message="New question",
        )
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "New question"

    def test_history_preserved(self):
        history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
        ]
        messages = build_chat_messages(system_prompt="S", history=history, user_message="Q3")
        # system + 4 истории + 1 пользовательское = 6
        assert len(messages) == 6

    def test_system_messages_in_history_are_dropped(self):
        history = [
            {"role": "system", "content": "Should be ignored"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        messages = build_chat_messages(system_prompt="S", history=history, user_message="Q")
        roles = [m["role"] for m in messages]
        assert roles.count("system") == 1  # только явный системный промпт

    def test_history_capped_at_20_turns(self):
        history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"msg{i}"} for i in range(50)]
        messages = build_chat_messages(system_prompt="S", history=history, user_message="Q")
        # system + до 20 истории + 1 новое пользовательское
        assert len(messages) <= 22
