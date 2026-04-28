"""
Асинхронный клиент для HTTP API Ollama.

Читает конфигурацию из переменных окружения:
  OLLAMA_BASE_URL  — базовый URL сервера Ollama (по умолчанию: http://localhost:11434)
  OLLAMA_TIMEOUT   — тайм-аут запроса в секундах (по умолчанию: 120)

Реализованы только эндпоинты, используемые данным сервисом:
  - /api/chat  (мультимодальный, потоковый)
"""
from __future__ import annotations

import base64
import json
import logging
import os
from typing import AsyncIterator

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


def _encode_image(image_bytes: bytes) -> str:
    """Возвращает base64-кодированную строку изображения, ожидаемую Ollama."""
    return base64.b64encode(image_bytes).decode("utf-8")


async def chat_completion(
    *,
    model: str,
    messages: list[dict],
    temperature: float = 0.2,
    stream: bool = False,
) -> dict:
    """
    Выполняет POST /api/chat и возвращает полный словарь ответа.

    Формат сообщений Ollama /api/chat:
      {"role": "user"|"assistant"|"system",
       "content": "...",
       "images": ["<base64>", ...]}   # опционально, только для vision

    Возвращает словарь ответа:
      {"model": ..., "message": {"role": "assistant", "content": "..."}, ...}

    Вызывает httpx.HTTPStatusError при ответах не из диапазона 2xx.
    Вызывает json.JSONDecodeError, если тело ответа не является корректным JSON.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
        },
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE_URL}/api/chat",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def chat_stream(
    *,
    model: str,
    messages: list[dict],
    temperature: float = 0.4,
) -> AsyncIterator[str]:
    """
    Выполняет POST /api/chat с stream=True и отдаёт текстовые фрагменты по мере поступления.

    Каждое отдаваемое значение — обычная текстовая строка (дельта-содержимое каждого
    потокового токена). Пустые строки никогда не отдаются.

    Вызывает httpx.HTTPStatusError при ответах не из диапазона 2xx.
    Вызывает ValueError, если строку не удаётся декодировать как JSON.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        async with client.stream(
            "POST",
            f"{_BASE_URL}/api/chat",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for raw_line in resp.aiter_lines():
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                try:
                    obj = json.loads(raw_line)
                except json.JSONDecodeError:
                    logger.warning("Ollama stream: could not decode line: %r", raw_line)
                    continue

                delta = obj.get("message", {}).get("content", "")
                if delta:
                    yield delta

                if obj.get("done"):
                    break
