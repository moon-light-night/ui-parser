"""Реализация gRPC ChatService."""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

import grpc
from sqlalchemy import desc, func, select, update

from app.db import AsyncSessionLocal
from app.models.db import (
    Analysis,
    ChatMessage,
    ChatSession,
    MessageRole,
    MessageStatus,
    Screenshot,
)
from app.grpc import analyzer_client
from app.redis_client import DB_FLUSH_INTERVAL, STREAM_TTL, get_redis

from .generated import chat_pb2, chat_pb2_grpc, common_pb2

logger = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_HISTORY_LIMIT = 20  # последние сообщения, передаваемые анализатору как контекст

# Максимальное время ожидания новых событий из Redis при ResumeMessageStream.
# Если за это время ничего не пришло и статус по-прежнему streaming —
# считаем генерацию потерянной.
_RESUME_MAX_IDLE_TICKS = 24   # 24 * 5 с = 120 с
_XREAD_BLOCK_MS = 5_000       # 5 с блокирующее чтение

# Набор работающих фоновых задач — предотвращает сборку мусора до завершения.
_running_tasks: set[asyncio.Task] = set()


# Вспомогательные функции

def _dt_to_ts(dt: datetime | None) -> common_pb2.Timestamp:
    if dt is None:
        return common_pb2.Timestamp(seconds=0, nanos=0)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ts = dt.timestamp()
    return common_pb2.Timestamp(seconds=int(ts), nanos=int((ts % 1) * 1_000_000_000))


_ROLE_TO_PROTO = {
    MessageRole.user: common_pb2.MESSAGE_ROLE_USER,
    MessageRole.assistant: common_pb2.MESSAGE_ROLE_ASSISTANT,
    MessageRole.system: common_pb2.MESSAGE_ROLE_SYSTEM,
}

_STATUS_TO_PROTO = {
    MessageStatus.completed: common_pb2.MESSAGE_STATUS_COMPLETED,
    MessageStatus.streaming: common_pb2.MESSAGE_STATUS_STREAMING,
    MessageStatus.failed: common_pb2.MESSAGE_STATUS_FAILED,
}


def _session_to_proto(row: ChatSession, message_count: int = 0) -> chat_pb2.ChatSession:
    return chat_pb2.ChatSession(
        id=str(row.id),
        screenshot_id=str(row.screenshot_id),
        title=row.title,
        message_count=message_count,
        created_at=_dt_to_ts(row.created_at),
        updated_at=_dt_to_ts(row.updated_at),
    )


def _message_to_proto(row: ChatMessage) -> chat_pb2.ChatMessage:
    return chat_pb2.ChatMessage(
        id=str(row.id),
        session_id=str(row.session_id),
        role=_ROLE_TO_PROTO.get(row.role, common_pb2.MESSAGE_ROLE_UNSPECIFIED),
        content=row.content,
        status=_STATUS_TO_PROTO.get(row.status, common_pb2.MESSAGE_STATUS_UNSPECIFIED),
        model_name=row.model_name or "",
        created_at=_dt_to_ts(row.created_at),
    )


def _error_event(code: str, message: str) -> chat_pb2.SendMessageEvent:
    return chat_pb2.SendMessageEvent(
        error=chat_pb2.ErrorEvent(code=code, message=message)
    )


# Фоновая задача генерации и публикации в Redis Stream

async def _generate_and_publish(
    *,
    assistant_msg_id: uuid.UUID,
    session_uuid: uuid.UUID,
    was_first_message: bool,
    user_content: str,
    screenshot_ctx: dict,
    analysis_ctx: dict | None,
    history_for_analyzer: list[dict],
    session_id_str: str,
) -> None:
    """
    Вызывает analyzer.GenerateChatReply и записывает события в Redis Stream.

    Работает независимо от клиентского gRPC-соединения: если клиент
    перезагрузит страницу до завершения, генерация продолжится и финальный
    ответ будет сохранён в Postgres.

    Redis Stream key: chat:msg:{assistant_msg_id}
    Поля записей:
      chunk  → {"type": "chunk",  "content": "<chunk>"}
      done   → {"type": "done",   "model": "<name>",   "session_title": "<opt>"}
      error  → {"type": "error",  "message": "<text>"}
    """
    stream_key = f"chat:msg:{assistant_msg_id}"
    redis = get_redis()

    full_response = ""
    model_used = "stub"
    stream_error: str | None = None
    chunk_count = 0

    try:
        async for event in analyzer_client.generate_chat_reply(
            session_id=session_id_str,
            screenshot_id=str(session_uuid),
            user_message=user_content,
            screenshot_context=screenshot_ctx,
            analysis_context=analysis_ctx,
            history=history_for_analyzer,
            model_name="gemma4:31b-cloud",
        ):
            if event.HasField("chunk"):
                chunk = event.chunk.text
                full_response += chunk
                chunk_count += 1

                # Публикуем чанк в Redis Stream.
                # maxlen=10000 — защита от бесконечного роста ключа.
                await redis.xadd(
                    stream_key,
                    {"type": "chunk", "content": chunk},
                    maxlen=10_000,
                )

                # Периодически сбрасываем накопленный контент в Postgres —
                # резервный вариант на случай истечения TTL Redis.
                if chunk_count % DB_FLUSH_INTERVAL == 0:
                    try:
                        async with AsyncSessionLocal() as db:
                            await db.execute(
                                update(ChatMessage)
                                .where(ChatMessage.id == assistant_msg_id)
                                .values(content=full_response)
                            )
                            await db.commit()
                    except Exception:
                        logger.warning(
                            "_generate_and_publish: periodic DB flush failed for msg %s",
                            assistant_msg_id,
                        )

            elif event.HasField("done"):
                full_response = event.done.full_response or full_response
                model_used = event.done.model_name or model_used

            elif event.HasField("error"):
                stream_error = f"{event.error.code}: {event.error.message}"
                break

    except Exception as exc:
        stream_error = str(exc)
        logger.exception(
            "_generate_and_publish: streaming error for assistant msg %s", assistant_msg_id
        )

    # Финализация: обновляем Postgres и публикуем итоговое событие в Redis
    if stream_error:
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(ChatMessage)
                    .where(ChatMessage.id == assistant_msg_id)
                    .values(status=MessageStatus.failed, content=full_response)
                )
                await db.commit()
        except Exception:
            logger.exception(
                "_generate_and_publish: failed to mark message %s as failed", assistant_msg_id
            )

        await redis.xadd(stream_key, {"type": "error", "message": stream_error})
        await redis.expire(stream_key, STREAM_TTL)
        return

    # Генерация заголовка сессии (только для первого сообщения)
    new_title = ""
    if was_first_message:
        try:
            generated = await analyzer_client.generate_title(user_message=user_content)
            if generated:
                new_title = generated
        except Exception:
            logger.warning("_generate_and_publish: generate_title failed, keeping existing title")

    # Сохраняем финальный ответ в Postgres
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(ChatMessage)
                .where(ChatMessage.id == assistant_msg_id)
                .values(
                    content=full_response,
                    status=MessageStatus.completed,
                    model_name=model_used,
                )
            )
            session_upd: dict = {"updated_at": datetime.now(timezone.utc)}
            if new_title:
                session_upd["title"] = new_title
            await db.execute(
                update(ChatSession)
                .where(ChatSession.id == session_uuid)
                .values(**session_upd)
            )
            await db.commit()
    except Exception:
        logger.exception(
            "_generate_and_publish: failed to persist assistant message %s", assistant_msg_id
        )

    # Публикуем событие завершения
    done_fields: dict = {"type": "done", "model": model_used}
    if new_title:
        done_fields["session_title"] = new_title
    await redis.xadd(stream_key, done_fields)
    await redis.expire(stream_key, STREAM_TTL)


# Вспомогательная функция: чтение Redis Stream и форвардинг событий клиенту

async def _forward_stream(
    *,
    stream_key: str,
    start_id: str,
    context: grpc.aio.ServicerContext,
    max_idle_ticks: int = _RESUME_MAX_IDLE_TICKS,
):
    """
    Читает Redis Stream начиная с start_id и выдаёт события SendMessageEvent.

    Используется в SendMessage (start_id="0") и ResumeMessageStream (start_id="0").
    """
    redis = get_redis()
    last_id = start_id
    idle_ticks = 0

    while True:
        if context.cancelled():
            return

        entries = await redis.xread({stream_key: last_id}, count=100, block=_XREAD_BLOCK_MS)

        if not entries:
            idle_ticks += 1
            if idle_ticks >= max_idle_ticks:
                yield _error_event("TIMEOUT", "Generation timed out or was lost")
                return
            continue

        idle_ticks = 0
        for _stream_name, messages in entries:
            for msg_id, fields in messages:
                last_id = msg_id
                event_type = fields.get("type", "")

                if event_type == "chunk":
                    yield chat_pb2.SendMessageEvent(
                        assistant_chunk=chat_pb2.AssistantChunkEvent(
                            chunk=fields.get("content", ""),
                        )
                    )

                elif event_type == "done":
                    # Финальное сообщение читаем из Postgres (там уже всё сохранено)
                    async with AsyncSessionLocal() as db:
                        # Ждём пока _generate_and_publish зафиксирует транзакцию
                        for _ in range(5):
                            row = await db.get(ChatMessage, uuid.UUID(stream_key.split(":")[-1]))
                            if row and row.status == MessageStatus.completed:
                                break
                            await asyncio.sleep(0.1)

                    yield chat_pb2.SendMessageEvent(
                        assistant_done=chat_pb2.AssistantDoneEvent(
                            message=_message_to_proto(row) if row else chat_pb2.ChatMessage(),
                            new_session_title=fields.get("session_title", ""),
                        )
                    )
                    return

                elif event_type == "error":
                    yield _error_event("INTERNAL", fields.get("message", "Generation failed"))
                    return


# Сервис

class ChatServicer(chat_pb2_grpc.ChatServiceServicer):

    # CreateSession

    async def CreateSession(
        self,
        request: chat_pb2.CreateSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.CreateSessionResponse:
        screenshot_id_str = request.screenshot_id.strip()
        if not screenshot_id_str:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "screenshot_id is required")

        try:
            screenshot_uuid = uuid.UUID(screenshot_id_str)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id format")

        async with AsyncSessionLocal() as db:
            exists = (await db.execute(
                select(Screenshot.id).where(Screenshot.id == screenshot_uuid)
            )).scalar_one_or_none()
            if exists is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "screenshot not found")

            title = (request.title or "").strip() or "New chat"
            session = ChatSession(
                id=uuid.uuid4(),
                screenshot_id=screenshot_uuid,
                title=title,
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)

        return chat_pb2.CreateSessionResponse(session=_session_to_proto(session, message_count=0))

    # ListSessions

    async def ListSessions(
        self,
        request: chat_pb2.ListSessionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.ListSessionsResponse:
        screenshot_id_str = request.screenshot_id.strip()
        if not screenshot_id_str:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "screenshot_id is required")

        try:
            screenshot_uuid = uuid.UUID(screenshot_id_str)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id format")

        page_size = min(
            request.pagination.page_size if request.pagination.page_size > 0 else _DEFAULT_PAGE_SIZE,
            _MAX_PAGE_SIZE,
        )
        offset = 0
        if request.pagination.page_token:
            try:
                offset = int(request.pagination.page_token)
            except ValueError:
                pass

        async with AsyncSessionLocal() as db:
            total_result = await db.execute(
                select(func.count())
                .select_from(ChatSession)
                .where(ChatSession.screenshot_id == screenshot_uuid)
            )
            total_count = total_result.scalar_one()

            rows_result = await db.execute(
                select(ChatSession, func.count(ChatMessage.id).label("msg_count"))
                .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
                .where(ChatSession.screenshot_id == screenshot_uuid)
                .group_by(ChatSession.id)
                .order_by(desc(ChatSession.updated_at))
                .offset(offset)
                .limit(page_size)
            )
            rows = rows_result.all()

        next_token = ""
        if offset + page_size < total_count:
            next_token = str(offset + page_size)

        return chat_pb2.ListSessionsResponse(
            sessions=[_session_to_proto(r.ChatSession, r.msg_count) for r in rows],
            pagination=common_pb2.PaginationResponse(
                next_page_token=next_token,
                total_count=total_count,
            ),
        )

    # GetSession

    async def GetSession(
        self,
        request: chat_pb2.GetSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.GetSessionResponse:
        session_id_str = request.session_id.strip()
        if not session_id_str:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "session_id is required")

        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid session_id format")

        async with AsyncSessionLocal() as db:
            row = (await db.execute(
                select(ChatSession, func.count(ChatMessage.id).label("msg_count"))
                .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
                .where(ChatSession.id == session_uuid)
                .group_by(ChatSession.id)
            )).first()

        if row is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, "session not found")

        return chat_pb2.GetSessionResponse(
            session=_session_to_proto(row.ChatSession, row.msg_count)
        )

    # DeleteSession

    async def DeleteSession(
        self,
        request: chat_pb2.DeleteSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.DeleteSessionResponse:
        session_id_str = request.session_id.strip()
        if not session_id_str:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "session_id is required")

        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid session_id format")

        async with AsyncSessionLocal() as db:
            row = await db.get(ChatSession, session_uuid)
            if row is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "session not found")
            await db.delete(row)
            await db.commit()

        return chat_pb2.DeleteSessionResponse(success=True)

    # ListMessages

    async def ListMessages(
        self,
        request: chat_pb2.ListMessagesRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.ListMessagesResponse:
        session_id_str = request.session_id.strip()
        if not session_id_str:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "session_id is required")

        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid session_id format")

        page_size = min(
            request.pagination.page_size if request.pagination.page_size > 0 else 50,
            200,
        )
        offset = 0
        if request.pagination.page_token:
            try:
                offset = int(request.pagination.page_token)
            except ValueError:
                pass

        async with AsyncSessionLocal() as db:
            total_result = await db.execute(
                select(func.count())
                .select_from(ChatMessage)
                .where(ChatMessage.session_id == session_uuid)
            )
            total_count = total_result.scalar_one()

            rows_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_uuid)
                .order_by(ChatMessage.created_at)
                .offset(offset)
                .limit(page_size)
            )
            messages = rows_result.scalars().all()

        next_token = ""
        if offset + page_size < total_count:
            next_token = str(offset + page_size)

        return chat_pb2.ListMessagesResponse(
            messages=[_message_to_proto(m) for m in messages],
            pagination=common_pb2.PaginationResponse(
                next_page_token=next_token,
                total_count=total_count,
            ),
        )

    # SendMessage — серверный стриминг с Redis Streams

    async def SendMessage(
        self,
        request: chat_pb2.SendMessageRequest,
        context: grpc.aio.ServicerContext,
    ):
        """
        Поток событий:
          1. Валидация и загрузка контекста из БД.
          2. Сохранение сообщения пользователя (status=completed).
          3. Создание сообщения ассистента (status=streaming, content="").
          4. Отправка MessageCreatedEvent клиенту.
          5. Запуск фоновой задачи _generate_and_publish (не зависит от соединения клиента).
          6. XREAD из Redis Stream — форвардинг чанков клиенту.
          7. По событию "done" — AssistantDoneEvent; по "error" — ErrorEvent.

        Если клиент перезагрузит страницу во время генерации, фоновая задача
        продолжит работу и запишет результат в Postgres. Клиент может
        получить ответ через ResumeMessageStream.
        """
        session_id_str = request.session_id.strip()
        content = request.content.strip()

        if not session_id_str:
            yield _error_event("INVALID_ARGUMENT", "session_id is required")
            return
        if not content:
            yield _error_event("INVALID_ARGUMENT", "content is required")
            return

        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            yield _error_event("INVALID_ARGUMENT", "invalid session_id format")
            return

        # Фаза 1: загрузка контекста и сохранение обоих сообщений
        user_msg: ChatMessage | None = None
        asst_msg: ChatMessage | None = None
        chat_session: ChatSession | None = None
        screenshot: Screenshot | None = None
        analysis: Analysis | None = None
        history_messages: list[ChatMessage] = []
        was_first_message: bool = True

        try:
            async with AsyncSessionLocal() as db:
                chat_session = (await db.execute(
                    select(ChatSession).where(ChatSession.id == session_uuid)
                )).scalar_one_or_none()

                if chat_session is None:
                    yield _error_event("NOT_FOUND", "session not found")
                    return

                screenshot = (await db.execute(
                    select(Screenshot).where(Screenshot.id == chat_session.screenshot_id)
                )).scalar_one_or_none()

                analysis = (await db.execute(
                    select(Analysis)
                    .where(Analysis.screenshot_id == chat_session.screenshot_id)
                    .order_by(desc(Analysis.created_at))
                    .limit(1)
                )).scalar_one_or_none()

                hist_rows = (await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == session_uuid)
                    .order_by(desc(ChatMessage.created_at))
                    .limit(_HISTORY_LIMIT)
                )).scalars().all()
                history_messages = list(reversed(hist_rows))
                was_first_message = len(history_messages) == 0

                # Сообщение пользователя
                now = datetime.now(timezone.utc)
                user_msg = ChatMessage(
                    id=uuid.uuid4(),
                    session_id=session_uuid,
                    role=MessageRole.user,
                    content=content,
                    status=MessageStatus.completed,
                    created_at=now,
                )
                db.add(user_msg)

                # Сообщение ассистента — создаём заранее со статусом streaming.
                # created_at смещён на 1 мс, чтобы при сортировке ассистент всегда
                # шёл после пользователя, даже если оба сообщения в одной транзакции.
                asst_msg = ChatMessage(
                    id=uuid.uuid4(),
                    session_id=session_uuid,
                    role=MessageRole.assistant,
                    content="",
                    status=MessageStatus.streaming,
                    created_at=now + timedelta(milliseconds=1),
                )
                db.add(asst_msg)

                await db.commit()
                await db.refresh(user_msg)
                await db.refresh(asst_msg)

        except Exception as exc:
            logger.exception("SendMessage: DB error during setup for session %s", session_id_str)
            yield _error_event("INTERNAL", f"Database error: {exc}")
            return

        # Фаза 2: отправка подтверждения сообщения пользователя
        yield chat_pb2.SendMessageEvent(
            message_created=chat_pb2.MessageCreatedEvent(
                message=_message_to_proto(user_msg)
            )
        )

        # Фаза 3: формирование контекста для анализатора
        screenshot_ctx = {
            "original_filename": screenshot.original_filename if screenshot else "",
            "mime_type": screenshot.mime_type if screenshot else "",
            "storage_bucket": screenshot.storage_bucket if screenshot else "",
            "storage_key": screenshot.storage_key if screenshot else "",
        }

        analysis_ctx: dict | None = None
        if analysis and analysis.result_json:
            analysis_ctx = {
                "screen_type": analysis.result_json.get("screen_type", ""),
                "summary": analysis.summary or analysis.result_json.get("summary", ""),
                "analysis_json": json.dumps(analysis.result_json),
            }

        history_for_analyzer = [
            {"role": m.role.value, "content": m.content}
            for m in history_messages
        ]

        # Фаза 4: запуск фоновой задачи генерации
        task = asyncio.create_task(
            _generate_and_publish(
                assistant_msg_id=asst_msg.id,
                session_uuid=session_uuid,
                was_first_message=was_first_message,
                user_content=content,
                screenshot_ctx=screenshot_ctx,
                analysis_ctx=analysis_ctx,
                history_for_analyzer=history_for_analyzer,
                session_id_str=session_id_str,
            )
        )
        _running_tasks.add(task)
        task.add_done_callback(_running_tasks.discard)

        # Фаза 5: читаем Redis Stream и форвардим события клиенту
        stream_key = f"chat:msg:{asst_msg.id}"
        async for event in _forward_stream(
            stream_key=stream_key,
            start_id="0",
            context=context,
        ):
            yield event

    # ResumeMessageStream — возобновление стрима после перезагрузки

    async def ResumeMessageStream(
        self,
        request: chat_pb2.ResumeMessageStreamRequest,
        context: grpc.aio.ServicerContext,
    ):
        """
        Позволяет клиенту переподключиться к генерации после перезагрузки страницы.

        Поведение по статусу сообщения:
          - completed: отдаём content из Postgres как AssistantDoneEvent (без стриминга).
          - failed:    отдаём ErrorEvent.
          - streaming: читаем Redis Stream с позиции "0" (все чанки с начала),
                       затем ждём финального события "done"/"error".
        """
        msg_id_str = request.message_id.strip()
        if not msg_id_str:
            yield _error_event("INVALID_ARGUMENT", "message_id is required")
            return

        try:
            msg_uuid = uuid.UUID(msg_id_str)
        except ValueError:
            yield _error_event("INVALID_ARGUMENT", "invalid message_id format")
            return

        async with AsyncSessionLocal() as db:
            asst_msg = await db.get(ChatMessage, msg_uuid)

        if asst_msg is None:
            yield _error_event("NOT_FOUND", "message not found")
            return

        if asst_msg.status == MessageStatus.completed:
            # Генерация уже завершена — возвращаем готовый результат.
            # Если content не пустой, отдаём его как один чанк перед done
            # чтобы не было пустого bubble на фронте.
            if asst_msg.content:
                yield chat_pb2.SendMessageEvent(
                    assistant_chunk=chat_pb2.AssistantChunkEvent(chunk=asst_msg.content)
                )
            yield chat_pb2.SendMessageEvent(
                assistant_done=chat_pb2.AssistantDoneEvent(
                    message=_message_to_proto(asst_msg),
                    new_session_title="",
                )
            )
            return

        if asst_msg.status == MessageStatus.failed:
            yield _error_event("GENERATION_FAILED", "Message generation failed")
            return

        # status == streaming: читаем Redis Stream
        stream_key = f"chat:msg:{asst_msg.id}"

        # Если в Redis нет записей вообще (stream ещё не создан или истёк TTL)
        # и в DB есть накопленный content — сначала отдаём его как replay.
        redis = get_redis()
        stream_len = await redis.xlen(stream_key)

        if stream_len == 0 and asst_msg.content:
            yield chat_pb2.SendMessageEvent(
                assistant_chunk=chat_pb2.AssistantChunkEvent(chunk=asst_msg.content)
            )
            # Дальше ждём финального события из Redis (или DB fallback ниже).

        async for event in _forward_stream(
            stream_key=stream_key,
            start_id="0",
            context=context,
        ):
            yield event
