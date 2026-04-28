"""Асинхронный gRPC-клиент для внутреннего AnalyzerService."""
from __future__ import annotations

import logging
import os
from typing import AsyncIterator

import grpc
import grpc.aio

from .generated import analyzer_pb2, analyzer_pb2_grpc

logger = logging.getLogger(__name__)

_ANALYZER_HOST = os.getenv("ANALYZER_GRPC_HOST_ADDR", "analyzer")
_ANALYZER_PORT = int(os.getenv("ANALYZER_GRPC_PORT", "50061"))
_ANALYZE_TIMEOUT = float(os.getenv("ANALYZE_TIMEOUT_SECONDS", "120"))


def _get_channel() -> grpc.aio.Channel:
    target = f"{_ANALYZER_HOST}:{_ANALYZER_PORT}"
    return grpc.aio.insecure_channel(target)


async def analyze_screenshot(
    *,
    screenshot_id: str,
    storage_bucket: str,
    storage_key: str,
    image_data: bytes | None = None,
    model_name: str = "gemma4:31b-cloud",
    analysis_mode: str = "full",
) -> analyzer_pb2.AnalyzeScreenshotResponse:
    """
    Вызывает сервис анализа для обработки скриншота.

    Передаёт расположение файла в хранилище, чтобы анализатор мог загрузить
    изображение самостоятельно. Опционально принимает готовые байты image_data,
    если бэкенд уже скачал файл (позволяет избежать повторного обращения к S3).

    Вызывает grpc.RpcError при транспортных ошибках или ошибках сервиса.
    Вызывает asyncio.TimeoutError, если анализатор не отвечает в срок.
    """
    request = analyzer_pb2.AnalyzeScreenshotRequest(
        screenshot_id=screenshot_id,
        storage_bucket=storage_bucket,
        storage_key=storage_key,
        image_data=image_data or b"",
        model_name=model_name,
        analysis_mode=analysis_mode,
    )

    async with _get_channel() as channel:
        stub = analyzer_pb2_grpc.AnalyzerServiceStub(channel)
        try:
            response: analyzer_pb2.AnalyzeScreenshotResponse = await stub.AnalyzeScreenshot(
                request,
                timeout=_ANALYZE_TIMEOUT,
            )
            return response
        except grpc.aio.AioRpcError as exc:
            logger.error(
                "AnalyzeScreenshot RPC failed: code=%s detail=%s",
                exc.code(),
                exc.details(),
            )
            raise


async def generate_chat_reply(
    *,
    session_id: str,
    screenshot_id: str,
    user_message: str,
    screenshot_context: dict | None = None,
    analysis_context: dict | None = None,
    history: list[dict] | None = None,
    model_name: str = "gemma4:31b-cloud",
) -> AsyncIterator[analyzer_pb2.GenerateChatReplyEvent]:
    """
    Асинхронный генератор, стримящий GenerateChatReplyEvent от анализатора.

    Канал остаётся открытым на всё время стриминга и закрывается
    в блоке finally после завершения или прерывания генератора.

    Генерирует analyzer_pb2.GenerateChatReplyEvent (chunk | done | error).
    Вызывает grpc.aio.AioRpcError при транспортных ошибках.
    """
    host = os.getenv("ANALYZER_GRPC_HOST_ADDR", "analyzer")
    port = int(os.getenv("ANALYZER_GRPC_PORT", "50061"))
    timeout = float(os.getenv("ANALYZE_TIMEOUT_SECONDS", "120"))

    screenshot_ctx = analyzer_pb2.ScreenshotContext(
        original_filename=(screenshot_context or {}).get("original_filename", ""),
        mime_type=(screenshot_context or {}).get("mime_type", ""),
        storage_bucket=(screenshot_context or {}).get("storage_bucket", ""),
        storage_key=(screenshot_context or {}).get("storage_key", ""),
    )
    analysis_ctx = analyzer_pb2.AnalysisContext(
        screen_type=(analysis_context or {}).get("screen_type", ""),
        summary=(analysis_context or {}).get("summary", ""),
        analysis_json=(analysis_context or {}).get("analysis_json", ""),
    )
    conv_history = [
        analyzer_pb2.ConversationMessage(role=m["role"], content=m["content"])
        for m in (history or [])
    ]
    request = analyzer_pb2.GenerateChatReplyRequest(
        session_id=session_id,
        screenshot_id=screenshot_id,
        screenshot_context=screenshot_ctx,
        analysis_context=analysis_ctx,
        history=conv_history,
        user_message=user_message,
        model_name=model_name,
    )

    channel = grpc.aio.insecure_channel(f"{host}:{port}")
    try:
        stub = analyzer_pb2_grpc.AnalyzerServiceStub(channel)
        async for event in stub.GenerateChatReply(request, timeout=timeout):
            yield event
    except grpc.aio.AioRpcError as exc:
        logger.error(
            "GenerateChatReply RPC failed: code=%s detail=%s",
            exc.code(),
            exc.details(),
        )
        raise
    finally:
        await channel.close()


async def generate_title(
    *,
    user_message: str,
    model_name: str = "",
) -> str:
    """
    Запрашивает у сервиса анализа короткий заголовок сессии на основе
    первого сообщения пользователя. Возвращает пустую строку при ошибке,
    чтобы вызывающий код мог сохранить существующий заголовок.
    """
    host = os.getenv("ANALYZER_GRPC_HOST_ADDR", "analyzer")
    port = int(os.getenv("ANALYZER_GRPC_PORT", "50061"))

    request = analyzer_pb2.GenerateTitleRequest(
        user_message=user_message,
        model_name=model_name,
    )

    async with grpc.aio.insecure_channel(f"{host}:{port}") as channel:
        stub = analyzer_pb2_grpc.AnalyzerServiceStub(channel)
        try:
            response: analyzer_pb2.GenerateTitleResponse = await stub.GenerateTitle(
                request,
                timeout=30.0,
            )
            if response.success and response.title:
                return response.title
            return ""
        except grpc.aio.AioRpcError as exc:
            logger.warning(
                "GenerateTitle RPC failed: code=%s detail=%s",
                exc.code(),
                exc.details(),
            )
            return ""
