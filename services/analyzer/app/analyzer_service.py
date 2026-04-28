"""
gRPC-сервисер AnalyzerService.

Переменная окружения ANALYZER_MODE управляет поведением:
  - "stub"   (по умолчанию): детерминированные фиктивные данные, Ollama не требуется
  - "ollama": вызывает Ollama VLM для реального анализа и контекстного чата

Ключевые переменные окружения:
  ANALYZER_MODE              stub | ollama
  OLLAMA_BASE_URL            http://host.docker.internal:11434
  OLLAMA_VISION_MODEL        модель с поддержкой зрения для AnalyzeScreenshot
  OLLAMA_CHAT_MODEL          текстовая модель для GenerateChatReply
  OLLAMA_TIMEOUT             секунды (по умолчанию 120)
  ANALYSIS_TIMEOUT_SECONDS   общий timeout gRPC-вызова (по умолчанию 60)
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid

import grpc

from app.storage import get_object_bytes
from app.ollama_client import chat_completion, chat_stream
from app.output_schema import parse_analysis_output
from app.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT,
    TITLE_SYSTEM_PROMPT,
    build_title_user_prompt,
    build_chat_system_prompt,
    build_chat_messages,
)

from .grpc.generated import analyzer_pb2, analyzer_pb2_grpc

logger = logging.getLogger(__name__)

_ANALYZER_MODE = os.getenv("ANALYZER_MODE", "stub")
_ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "60"))
_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud"))
_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud"))

# Stub-анализ — реалистично выглядящий структурированный вывод для разработки/тестирования

_STUB_RESPONSE = {
    "screen_type": "dashboard",
    "summary": (
        "A data-heavy dashboard with multiple metric cards and a navigation sidebar. "
        "The layout prioritises information density over visual breathing room."
    ),
    "sections": [
        {"name": "Top navigation", "description": "Primary nav bar with logo, search, and profile controls"},
        {"name": "Metric cards row", "description": "Four KPI summary cards displayed horizontally"},
        {"name": "Main chart area", "description": "Line chart occupying the central content area"},
        {"name": "Sidebar", "description": "Left-aligned filter and navigation panel"},
    ],
    "ui_issues": [
        {
            "title": "Low contrast on secondary text",
            "severity": "medium",
            "description": "Secondary labels and captions use a gray that does not meet WCAG AA contrast ratio (4.5:1) against the white background.",
            "evidence": "Chart axis labels and card subtitles appear in #9CA3AF on #FFFFFF",
            "recommendation": "Use at least #6B7280 for body text or increase background contrast.",
        },
        {
            "title": "No visible focus state on interactive elements",
            "severity": "high",
            "description": "Keyboard users cannot determine which element is focused. Focus outlines appear to be suppressed globally.",
            "evidence": "Tab navigation does not reveal any visible focus ring on buttons or links",
            "recommendation": "Restore or add a 2px outline focus indicator that meets WCAG 2.4.7.",
        },
        {
            "title": "Metric cards lack loading skeleton",
            "severity": "low",
            "description": "When data is loading, cards show blank space instead of a skeleton placeholder, causing layout shift.",
            "evidence": "Cards collapse to minimal height during fetch",
            "recommendation": "Add shimmer skeleton placeholders matching the card structure.",
        },
    ],
    "ux_suggestions": [
        {
            "title": "Add date range quick-select presets",
            "description": "Users frequently filter by last 7 / 30 / 90 days. Preset buttons reduce friction compared to the current date picker.",
        },
        {
            "title": "Highlight the primary call-to-action",
            "description": "The main action button shares the same visual weight as secondary controls. Use a filled primary color to make it dominant.",
        },
        {
            "title": "Group related filters visually",
            "description": "The sidebar contains 12 independent filters with no grouping. Collapsible sections would reduce cognitive load.",
        },
    ],
    "implementation_tasks": [
        {
            "title": "Fix text contrast for WCAG AA compliance",
            "description": "Update the Tailwind CSS color palette tokens used for secondary text from gray-400 to gray-500 or darker.",
            "priority": "high",
        },
        {
            "title": "Implement focus-visible styles",
            "description": "Remove outline:none overrides and add a consistent focus-visible ring using Tailwind's ring utilities.",
            "priority": "high",
        },
        {
            "title": "Add loading skeleton to metric cards",
            "description": "Create a SkeletonCard component that mirrors the card layout and display it during data fetch.",
            "priority": "medium",
        },
        {
            "title": "Add date range quick-select buttons",
            "description": "Add preset buttons (7d / 30d / 90d / YTD) above the chart filter area.",
            "priority": "medium",
        },
    ],
}


class AnalyzerServicer(analyzer_pb2_grpc.AnalyzerServiceServicer):

    async def AnalyzeScreenshot(
        self,
        request: analyzer_pb2.AnalyzeScreenshotRequest,
        context: grpc.aio.ServicerContext,
    ) -> analyzer_pb2.AnalyzeScreenshotResponse:
        screenshot_id = request.screenshot_id or str(uuid.uuid4())
        model_name = request.model_name or "gemma4:31b-cloud"

        # Получаем байты изображения (нужны для реального вызова Ollama; в stub-режиме игнорируются)
        image_data = request.image_data
        if not image_data and request.storage_bucket and request.storage_key:
            try:
                image_data = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: get_object_bytes(request.storage_bucket, request.storage_key),
                )
            except Exception as exc:
                logger.warning(
                    "Could not fetch image from S3 (%s/%s): %s",
                    request.storage_bucket,
                    request.storage_key,
                    exc,
                )

        if _ANALYZER_MODE == "ollama":
            return await self._analyze_with_ollama(
                screenshot_id, model_name, image_data, request.analysis_mode, context
            )

        return self._build_stub_response(screenshot_id)

    # Stub-режим

    def _build_stub_response(self, screenshot_id: str) -> analyzer_pb2.AnalyzeScreenshotResponse:
        data = _STUB_RESPONSE

        sections = [
            analyzer_pb2.Section(name=s["name"], description=s["description"])
            for s in data["sections"]
        ]
        ui_issues = [
            analyzer_pb2.Issue(
                title=i["title"],
                severity=i["severity"],
                description=i["description"],
                evidence=i["evidence"],
                recommendation=i["recommendation"],
            )
            for i in data["ui_issues"]
        ]
        suggestions = [
            analyzer_pb2.Suggestion(title=s["title"], description=s["description"])
            for s in data["ux_suggestions"]
        ]
        tasks = [
            analyzer_pb2.Task(title=t["title"], description=t["description"], priority=t["priority"])
            for t in data["implementation_tasks"]
        ]

        return analyzer_pb2.AnalyzeScreenshotResponse(
            analysis_id=str(uuid.uuid4()),
            screen_type=data["screen_type"],
            summary=data["summary"],
            sections=sections,
            ui_issues=ui_issues,
            ux_suggestions=suggestions,
            implementation_tasks=tasks,
            raw_json=json.dumps(data),
            success=True,
        )

    # Анализ с использованием Ollama vision

    async def _analyze_with_ollama(
        self,
        screenshot_id: str,
        model_name: str,
        image_data: bytes,
        analysis_mode: str,
        context: grpc.aio.ServicerContext,
    ) -> analyzer_pb2.AnalyzeScreenshotResponse:
        if not image_data:
            logger.error("AnalyzeScreenshot(ollama): no image data for %s", screenshot_id)
            return analyzer_pb2.AnalyzeScreenshotResponse(
                analysis_id=str(uuid.uuid4()),
                success=False,
                error_message="Image data is required for Ollama analysis",
            )

        effective_model = model_name or _VISION_MODEL
        image_b64 = base64.b64encode(image_data).decode("utf-8")

        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ANALYSIS_USER_PROMPT,
                "images": [image_b64],
            },
        ]

        try:
            response = await chat_completion(
                model=effective_model,
                messages=messages,
                temperature=0.1,   # низкая температура для детерминированного структурированного вывода
            )
        except Exception as exc:
            logger.exception("Ollama chat_completion failed for %s", screenshot_id)
            return analyzer_pb2.AnalyzeScreenshotResponse(
                analysis_id=str(uuid.uuid4()),
                success=False,
                error_message=f"Ollama request failed: {exc}",
            )

        raw_content: str = response.get("message", {}).get("content", "")
        logger.debug("Ollama raw output (%d chars): %.200s", len(raw_content), raw_content)

        parsed = parse_analysis_output(raw_content)

        sections = [
            analyzer_pb2.Section(name=s.name, description=s.description)
            for s in parsed.sections
        ]
        ui_issues = [
            analyzer_pb2.Issue(
                title=i.title,
                severity=i.severity,
                description=i.description,
                evidence=i.evidence,
                recommendation=i.recommendation,
            )
            for i in parsed.ui_issues
        ]
        suggestions = [
            analyzer_pb2.Suggestion(title=s.title, description=s.description)
            for s in parsed.ux_suggestions
        ]
        tasks = [
            analyzer_pb2.Task(title=t.title, description=t.description, priority=t.priority)
            for t in parsed.implementation_tasks
        ]

        return analyzer_pb2.AnalyzeScreenshotResponse(
            analysis_id=str(uuid.uuid4()),
            screen_type=parsed.screen_type,
            summary=parsed.summary,
            sections=sections,
            ui_issues=ui_issues,
            ux_suggestions=suggestions,
            implementation_tasks=tasks,
            raw_json=parsed.model_dump_json(),
            success=True,
        )

    # GenerateChatReply — потоковая передача через Ollama / stub-fallback

    async def GenerateChatReply(self, request, context):
        """
        Потоковый ответ чата, основанный на анализе скриншота.

        В режиме ollama:
          - формирует системный промпт, включающий screen_type, summary и
            полный JSON анализа (проблемы, задачи, предложения, секции)
          - передаёт ответ токен за токеном через потоковый /api/chat Ollama
          - при любой транспортной или модельной ошибке переключается на stub

        В stub-режиме:
          - генерирует контекстный детерминированный ответ на основе полей запроса
        """
        user_msg = (request.user_message or "").strip()
        if not user_msg:
            return

        screen_type = ""
        summary = ""
        analysis_json = ""
        original_filename = ""

        if request.HasField("screenshot_context"):
            original_filename = request.screenshot_context.original_filename or ""
        if request.HasField("analysis_context"):
            screen_type = request.analysis_context.screen_type or ""
            summary = request.analysis_context.summary or ""
            analysis_json = request.analysis_context.analysis_json or ""

        history = [
            {"role": m.role, "content": m.content}
            for m in request.history
        ]

        # Через Ollama
        if _ANALYZER_MODE == "ollama":
            system_prompt = build_chat_system_prompt(
                original_filename=original_filename,
                screen_type=screen_type,
                summary=summary,
                analysis_json=analysis_json,
            )
            messages = build_chat_messages(
                system_prompt=system_prompt,
                history=history,
                user_message=user_msg,
            )
            effective_model = _CHAT_MODEL

            full_response = ""
            chunk_index = 0
            ollama_failed = False

            try:
                async for text_chunk in chat_stream(
                    model=effective_model,
                    messages=messages,
                    temperature=0.4,
                ):
                    full_response += text_chunk
                    yield analyzer_pb2.GenerateChatReplyEvent(
                        chunk=analyzer_pb2.ChunkEvent(text=text_chunk, index=chunk_index)
                    )
                    chunk_index += 1

            except Exception as exc:
                logger.exception("Ollama chat stream failed — falling back to error event")
                ollama_failed = True
                yield analyzer_pb2.GenerateChatReplyEvent(
                    error=analyzer_pb2.ErrorEvent(
                        code="OLLAMA_ERROR",
                        message=f"Ollama request failed: {exc}",
                    )
                )

            if not ollama_failed:
                yield analyzer_pb2.GenerateChatReplyEvent(
                    done=analyzer_pb2.DoneEvent(
                        full_response=full_response,
                        model_name=effective_model,
                        total_tokens=chunk_index,
                    )
                )
            return

        # Через Stub — контекстный детерминированный текст
        if screen_type or summary:
            short_summary = (summary[:150] + "…") if len(summary) > 150 else summary
            stub_text = (
                f"You are looking at a {screen_type or 'UI'} screen. "
                f"The analysis summary: {short_summary} "
                f"Regarding your question — \"{user_msg[:100]}{'…' if len(user_msg) > 100 else ''}\" — "
                "I can see several aspects worth discussing based on the stored analysis. "
                "Switch ANALYZER_MODE=ollama and ensure an Ollama vision model is running "
                "to get specific, image-grounded answers."
            )
        else:
            stub_text = (
                f"You asked: \"{user_msg[:120]}{'…' if len(user_msg) > 120 else ''}\". "
                "No analysis context is attached to this session yet. "
                "Run an analysis first so I can give you feedback grounded in the screenshot. "
                "Once analysis is complete I will reference exact sections, issues, and suggestions."
            )

        words = stub_text.split()
        full_response = ""
        for i, word in enumerate(words):
            chunk_text = word + (" " if i < len(words) - 1 else "")
            full_response += chunk_text
            yield analyzer_pb2.GenerateChatReplyEvent(
                chunk=analyzer_pb2.ChunkEvent(text=chunk_text, index=i)
            )
            await asyncio.sleep(0.03)

        yield analyzer_pb2.GenerateChatReplyEvent(
            done=analyzer_pb2.DoneEvent(
                full_response=full_response.strip(),
                model_name="stub",
                total_tokens=len(words),
            )
        )

    # GenerateTitle — краткий заголовок сессии по первому сообщению пользователя

    async def GenerateTitle(
        self,
        request: analyzer_pb2.GenerateTitleRequest,
        context: grpc.aio.ServicerContext,
    ) -> analyzer_pb2.GenerateTitleResponse:
        user_message = (request.user_message or "").strip()
        if not user_message:
            return analyzer_pb2.GenerateTitleResponse(
                title="New chat",
                success=True,
            )

        if _ANALYZER_MODE == "ollama":
            try:
                effective_model = request.model_name or _CHAT_MODEL
                messages = [
                    {"role": "system", "content": TITLE_SYSTEM_PROMPT},
                    {"role": "user", "content": build_title_user_prompt(user_message)},
                ]
                response = await chat_completion(
                    model=effective_model,
                    messages=messages,
                    temperature=0.3,
                )
                raw: str = response.get("message", {}).get("content", "").strip()
                # Убираем кавычки и завершающие знаки препинания, которые может добавить модель
                title = raw.strip('"\'').rstrip(".!?,;").strip()
                title = title[:80] if title else "New chat"
                return analyzer_pb2.GenerateTitleResponse(title=title, success=True)
            except Exception as exc:
                logger.exception("GenerateTitle: Ollama call failed")
                return analyzer_pb2.GenerateTitleResponse(
                    title="",
                    success=False,
                    error_message=str(exc),
                )

        # Stub: формируем заголовок из первых нескольких слов сообщения
        words = user_message.split()
        stub_title = " ".join(words[:6])
        if len(words) > 6:
            stub_title += "…"
        return analyzer_pb2.GenerateTitleResponse(title=stub_title, success=True)
