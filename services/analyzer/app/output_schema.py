"""
Pydantic-модели для структурированного вывода анализа из Ollama.

Модель инструктируется возвращать строгий JSON, соответствующий AnalysisOutput.
Если модель возвращает некорректный или частичный JSON, NormalisedAnalysis.from_raw()
пытается восстановить данные по мере возможности, прежде чем перейти к безопасным значениям по умолчанию.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)

# Ожидаемая форма JSON

class SectionItem(BaseModel):
    name: str = Field(default="")
    description: str = Field(default="")


class UiIssueItem(BaseModel):
    title: str = Field(default="")
    severity: Literal["low", "medium", "high"] = Field(default="medium")
    description: str = Field(default="")
    evidence: str = Field(default="")
    recommendation: str = Field(default="")

    @field_validator("severity", mode="before")
    @classmethod
    def normalise_severity(cls, v: object) -> str:
        if isinstance(v, str) and v.lower() in {"low", "medium", "high"}:
            return v.lower()
        return "medium"


class UxSuggestionItem(BaseModel):
    title: str = Field(default="")
    description: str = Field(default="")


class ImplementationTaskItem(BaseModel):
    title: str = Field(default="")
    description: str = Field(default="")
    priority: Literal["low", "medium", "high"] = Field(default="medium")

    @field_validator("priority", mode="before")
    @classmethod
    def normalise_priority(cls, v: object) -> str:
        if isinstance(v, str) and v.lower() in {"low", "medium", "high"}:
            return v.lower()
        return "medium"


_SCREEN_TYPES = {
    "landing_page", "dashboard", "form", "settings",
    "modal", "mobile_screen", "unknown",
}


class AnalysisOutput(BaseModel):
    screen_type: str = Field(default="unknown")
    summary: str = Field(default="")
    sections: list[SectionItem] = Field(default_factory=list)
    ui_issues: list[UiIssueItem] = Field(default_factory=list)
    ux_suggestions: list[UxSuggestionItem] = Field(default_factory=list)
    implementation_tasks: list[ImplementationTaskItem] = Field(default_factory=list)

    @field_validator("screen_type", mode="before")
    @classmethod
    def normalise_screen_type(cls, v: object) -> str:
        if isinstance(v, str) and v.lower() in _SCREEN_TYPES:
            return v.lower()
        return "unknown"


# Извлечение JSON из сырого вывода модели по мере возможности

def _extract_json_block(text: str) -> str:
    """
    Пытается выделить JSON-объект из вывода модели, который может быть обёрнут
    в markdown-блоки кода или содержать предшествующий/завершающий текст.
    """
    # Убираем markdown-блоки кода
    fence = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fence:
        return fence.group(1).strip()

    # Берём первый блок {...}
    brace = re.search(r"\{[\s\S]*\}", text)
    if brace:
        return brace.group(0)

    return text.strip()


def parse_analysis_output(raw_text: str) -> AnalysisOutput:
    """
    Разбирает сырой вывод модели в валидированный AnalysisOutput.

    Стратегия:
    1. Убираем блоки кода / текст, чтобы выделить JSON.
    2. Разбираем с помощью json.loads.
    3. Валидируем через Pydantic (мягкая — неизвестные поля игнорируются).
    4. При любой ошибке возвращаем минимальное безопасное значение по умолчанию с сырым текстом в summary.
    """
    extracted = _extract_json_block(raw_text)
    try:
        data = json.loads(extracted)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Could not parse model output as JSON (%s); returning fallback", exc)
        return AnalysisOutput(
            screen_type="unknown",
            summary=raw_text[:500] if raw_text else "Model returned non-JSON output.",
        )

    try:
        return AnalysisOutput.model_validate(data)
    except ValidationError as exc:
        logger.warning("Model output failed Pydantic validation: %s", exc)
        # Пытаемся частично восстановить данные: берём что можно, для остального используем умолчания Pydantic
        safe: dict = {}
        for field_name in AnalysisOutput.model_fields:
            if field_name in data:
                safe[field_name] = data[field_name]
        try:
            return AnalysisOutput.model_validate(safe)
        except ValidationError:
            return AnalysisOutput(
                summary=data.get("summary", raw_text[:300]),
            )
