"""Async Redis client singleton for chat stream events."""
from __future__ import annotations

import os

import redis.asyncio as aioredis

_client: aioredis.Redis | None = None

# TTL потоков Redis для сообщений чата (в секундах).
# По истечении этого периода потоки истекают, поэтому ключи не накапливаются бесконечно.
STREAM_TTL = 7_200  # 2 hours

# Как часто (чанками) записывать накопленное содержимое обратно в Postgres.
# Действует как резервный вариант, если поток истекает до попытки возобновления.
DB_FLUSH_INTERVAL = 20


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _client = aioredis.from_url(url, decode_responses=True)
    return _client
