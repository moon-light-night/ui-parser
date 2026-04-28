"""Реализация gRPC ScreenshotService."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

import grpc
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import grpc.aio

from app.db import AsyncSessionLocal
from app.models.db import (
    Analysis,
    ChatSession,
    Screenshot,
    ScreenshotStatus,
)
from app.storage import ALLOWED_MIME_TYPES, create_presigned_upload_url, delete_s3_object
from app.grpc import analyzer_client

from .generated import common_pb2, screenshot_pb2, screenshot_pb2_grpc

logger = logging.getLogger(__name__)

_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100

# Реестр asyncio.Event для активных задач анализа: screenshot_id → Event.
# Позволяет RunAnalysis-стримам ждать завершения без поллинга БД.
# При завершении задачи (_run_analysis_and_notify) событие взводится и удаляется из реестра.
_analysis_done: dict[uuid.UUID, asyncio.Event] = {}


def _dt_to_ts(dt: datetime | None) -> common_pb2.Timestamp:
    if dt is None:
        return common_pb2.Timestamp(seconds=0, nanos=0)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ts = dt.timestamp()
    return common_pb2.Timestamp(seconds=int(ts), nanos=int((ts % 1) * 1_000_000_000))


def _status_to_proto(status: ScreenshotStatus) -> common_pb2.ScreenshotStatus:
    mapping = {
        ScreenshotStatus.uploaded: common_pb2.SCREENSHOT_STATUS_UPLOADED,
        ScreenshotStatus.analyzing: common_pb2.SCREENSHOT_STATUS_ANALYZING,
        ScreenshotStatus.completed: common_pb2.SCREENSHOT_STATUS_COMPLETED,
        ScreenshotStatus.failed: common_pb2.SCREENSHOT_STATUS_FAILED,
    }
    return mapping.get(status, common_pb2.SCREENSHOT_STATUS_UNSPECIFIED)


def _screenshot_to_proto(row: Screenshot) -> screenshot_pb2.Screenshot:
    return screenshot_pb2.Screenshot(
        id=str(row.id),
        title=row.title or "",
        original_filename=row.original_filename,
        mime_type=row.mime_type,
        file_size=row.file_size,
        storage_bucket=row.storage_bucket,
        storage_key=row.storage_key,
        storage_region=row.storage_region or "",
        storage_url=row.storage_url or "",
        status=_status_to_proto(row.status),
        created_at=_dt_to_ts(row.created_at),
        updated_at=_dt_to_ts(row.updated_at),
    )


def _analysis_to_proto(row: Analysis) -> screenshot_pb2.Analysis:
    result = row.result_json or {}

    sections = [
        screenshot_pb2.AnalysisSection(
            name=s.get("name", ""), description=s.get("description", "")
        )
        for s in result.get("sections", [])
    ]

    severity_map = {
        "low": common_pb2.SEVERITY_LOW,
        "medium": common_pb2.SEVERITY_MEDIUM,
        "high": common_pb2.SEVERITY_HIGH,
    }
    ui_issues = [
        screenshot_pb2.UiIssue(
            title=i.get("title", ""),
            severity=severity_map.get(i.get("severity", ""), common_pb2.SEVERITY_UNSPECIFIED),
            description=i.get("description", ""),
            evidence=i.get("evidence", ""),
            recommendation=i.get("recommendation", ""),
        )
        for i in result.get("ui_issues", [])
    ]

    ux_suggestions = [
        screenshot_pb2.UxSuggestion(
            title=s.get("title", ""), description=s.get("description", "")
        )
        for s in result.get("ux_suggestions", [])
    ]

    priority_map = {
        "low": common_pb2.PRIORITY_LOW,
        "medium": common_pb2.PRIORITY_MEDIUM,
        "high": common_pb2.PRIORITY_HIGH,
    }
    tasks = [
        screenshot_pb2.ImplementationTask(
            title=t.get("title", ""),
            description=t.get("description", ""),
            priority=priority_map.get(t.get("priority", ""), common_pb2.PRIORITY_UNSPECIFIED),
        )
        for t in result.get("implementation_tasks", [])
    ]

    return screenshot_pb2.Analysis(
        id=str(row.id),
        screenshot_id=str(row.screenshot_id),
        model_name=row.model_name,
        screen_type=result.get("screen_type", ""),
        summary=row.summary or result.get("summary", ""),
        sections=sections,
        ui_issues=ui_issues,
        ux_suggestions=ux_suggestions,
        implementation_tasks=tasks,
        error_message=row.error_message or "",
        created_at=_dt_to_ts(row.created_at),
        updated_at=_dt_to_ts(row.updated_at),
    )


class ScreenshotServicer(screenshot_pb2_grpc.ScreenshotServiceServicer):

    async def CreateUploadUrl(
        self,
        request: screenshot_pb2.CreateUploadUrlRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.CreateUploadUrlResponse:
        filename = request.filename.strip()
        mime_type = request.mime_type.strip()
        file_size = request.file_size

        if not filename:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "filename is required")
        if mime_type not in ALLOWED_MIME_TYPES:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Unsupported mime type. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
            )
        if file_size <= 0 or file_size > _MAX_FILE_SIZE:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"file_size must be 1–{_MAX_FILE_SIZE} bytes",
            )

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: create_presigned_upload_url(filename, mime_type, file_size),
            )
        except Exception as exc:
            logger.exception("Failed to create presigned URL")
            await context.abort(grpc.StatusCode.INTERNAL, str(exc))

        return screenshot_pb2.CreateUploadUrlResponse(
            upload_url=result["upload_url"],
            storage_bucket=result["bucket"],
            storage_key=result["key"],
            expires_at=int(result["expires_at"]),
        )

    async def RegisterScreenshot(
        self,
        request: screenshot_pb2.RegisterScreenshotRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.RegisterScreenshotResponse:
        if not request.original_filename:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "original_filename is required")
        if not request.storage_bucket or not request.storage_key:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "storage_bucket and storage_key are required")
        if request.mime_type not in ALLOWED_MIME_TYPES:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "unsupported mime_type")
        if request.file_size <= 0:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "file_size must be positive")

        async with AsyncSessionLocal() as session:
            screenshot = Screenshot(
                id=uuid.uuid4(),
                title=request.title or None,
                original_filename=request.original_filename,
                mime_type=request.mime_type,
                file_size=request.file_size,
                storage_bucket=request.storage_bucket,
                storage_key=request.storage_key,
                status=ScreenshotStatus.uploaded,
            )
            session.add(screenshot)
            await session.commit()
            await session.refresh(screenshot)

        return screenshot_pb2.RegisterScreenshotResponse(
            screenshot=_screenshot_to_proto(screenshot)
        )

    async def ListScreenshots(
        self,
        request: screenshot_pb2.ListScreenshotsRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.ListScreenshotsResponse:
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

        async with AsyncSessionLocal() as session:
            total_result = await session.execute(select(func.count()).select_from(Screenshot))
            total_count = total_result.scalar_one()

            rows_result = await session.execute(
                select(Screenshot)
                .order_by(desc(Screenshot.created_at))
                .offset(offset)
                .limit(page_size)
            )
            rows = rows_result.scalars().all()

        next_token = ""
        if offset + page_size < total_count:
            next_token = str(offset + page_size)

        return screenshot_pb2.ListScreenshotsResponse(
            screenshots=[_screenshot_to_proto(r) for r in rows],
            pagination=common_pb2.PaginationResponse(
                next_page_token=next_token,
                total_count=total_count,
            ),
        )

    async def GetScreenshot(
        self,
        request: screenshot_pb2.GetScreenshotRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.GetScreenshotResponse:
        try:
            screenshot_id = uuid.UUID(request.screenshot_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id UUID")

        async with AsyncSessionLocal() as session:
            row = await session.get(Screenshot, screenshot_id)

        if row is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, "screenshot not found")

        return screenshot_pb2.GetScreenshotResponse(screenshot=_screenshot_to_proto(row))

    async def StartAnalysis(
        self,
        request: screenshot_pb2.StartAnalysisRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.StartAnalysisResponse:
        try:
            screenshot_id = uuid.UUID(request.screenshot_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id UUID")

        model_name = request.model_name or "gemma4:31b-cloud"

        async with AsyncSessionLocal() as session:
            screenshot = await session.get(Screenshot, screenshot_id)
            if screenshot is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "screenshot not found")

            if screenshot.status == ScreenshotStatus.analyzing:
                # Анализ уже выполняется — возвращаем текущий статус
                return screenshot_pb2.StartAnalysisResponse(
                    analysis_id="",
                    status=_status_to_proto(screenshot.status),
                )

            analysis = Analysis(
                id=uuid.uuid4(),
                screenshot_id=screenshot_id,
                model_name=model_name,
            )
            session.add(analysis)
            screenshot.status = ScreenshotStatus.analyzing
            await session.commit()
            await session.refresh(analysis)
            analysis_id = str(analysis.id)

        # Фоновая задача без ожидания — вызывает реальный сервис анализа
        asyncio.create_task(
            _run_analysis(screenshot_id, analysis.id, model_name, screenshot.storage_bucket, screenshot.storage_key)
        )

        return screenshot_pb2.StartAnalysisResponse(
            analysis_id=analysis_id,
            status=common_pb2.SCREENSHOT_STATUS_ANALYZING,
        )

    async def GetLatestAnalysis(
        self,
        request: screenshot_pb2.GetLatestAnalysisRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.GetLatestAnalysisResponse:
        try:
            screenshot_id = uuid.UUID(request.screenshot_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id UUID")

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Analysis)
                .where(Analysis.screenshot_id == screenshot_id)
                .order_by(desc(Analysis.created_at))
                .limit(1)
            )
            row = result.scalar_one_or_none()

        if row is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, "no analysis found for this screenshot")

        return screenshot_pb2.GetLatestAnalysisResponse(analysis=_analysis_to_proto(row))

    async def DeleteScreenshot(
        self,
        request: screenshot_pb2.DeleteScreenshotRequest,
        context: grpc.aio.ServicerContext,
    ) -> screenshot_pb2.DeleteScreenshotResponse:
        try:
            screenshot_id = uuid.UUID(request.screenshot_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id UUID")

        async with AsyncSessionLocal() as session:
            screenshot = await session.get(Screenshot, screenshot_id)
            if screenshot is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "screenshot not found")

            storage_bucket = screenshot.storage_bucket
            storage_key = screenshot.storage_key
            await session.delete(screenshot)
            await session.commit()

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: delete_s3_object(storage_bucket, storage_key),
            )
        except Exception:
            logger.exception(
                "Failed to delete S3 object %s/%s (DB record already deleted)",
                storage_bucket,
                storage_key,
            )

        return screenshot_pb2.DeleteScreenshotResponse()

    async def RunAnalysis(
        self,
        request: screenshot_pb2.RunAnalysisRequest,
        context: grpc.aio.ServicerContext,
    ):
        """
        Серверный стриминг анализа. Поведение зависит от текущего статуса скриншота:
          - uploaded/completed/failed → запускает новый анализ.
          - analyzing → присоединяется к уже идущему анализу через asyncio.Event
            (без поллинга БД). Используется при перезагрузке страницы.
        """
        try:
            screenshot_id = uuid.UUID(request.screenshot_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "invalid screenshot_id UUID")

        model_name = request.model_name or "gemma4:31b-cloud"

        async with AsyncSessionLocal() as session:
            screenshot = await session.get(Screenshot, screenshot_id)
            if screenshot is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "screenshot not found")

            status = screenshot.status

            # --- Присоединение к уже идущему анализу ---
            if status == ScreenshotStatus.analyzing:
                event = _analysis_done.get(screenshot_id)
                if event is None:
                    # Сервер перезапустился во время анализа — задача потеряна
                    await context.abort(
                        grpc.StatusCode.UNAVAILABLE,
                        "анализ запущен до перезапуска сервера; повторите позже",
                    )
                # Ждём завершения без поллинга
                try:
                    await asyncio.shield(event.wait())
                except asyncio.CancelledError:
                    raise
                async with AsyncSessionLocal() as s2:
                    yield (await _read_result_event(s2, screenshot_id))
                return

        # --- Новый анализ (uploaded / completed / failed) ---
        async with AsyncSessionLocal() as session:
            screenshot = await session.get(Screenshot, screenshot_id)
            analysis = Analysis(
                id=uuid.uuid4(),
                screenshot_id=screenshot_id,
                model_name=model_name,
            )
            session.add(analysis)
            screenshot.status = ScreenshotStatus.analyzing
            await session.commit()
            await session.refresh(analysis)
            storage_bucket = screenshot.storage_bucket
            storage_key = screenshot.storage_key
            analysis_id = analysis.id

        # Регистрируем Event до запуска задачи, чтобы исключить гонку
        event = asyncio.Event()
        _analysis_done[screenshot_id] = event

        yield screenshot_pb2.RunAnalysisEvent(
            started=screenshot_pb2.RunAnalysisStartedEvent(analysis_id=str(analysis_id))
        )

        asyncio.create_task(
            _run_analysis_and_notify(
                screenshot_id, analysis_id, model_name, storage_bucket, storage_key
            )
        )

        try:
            await asyncio.shield(event.wait())
        except asyncio.CancelledError:
            # Клиент отключился — задача продолжает работу, Event будет взведён по завершении
            logger.info(
                "RunAnalysis: клиент отключился для скриншота %s, задача продолжается в фоне",
                screenshot_id,
            )
            raise

        async with AsyncSessionLocal() as session:
            yield (await _read_result_event(session, screenshot_id, analysis_id=analysis_id))
        logger.info("RunAnalysis: завершён для скриншота %s", screenshot_id)



async def _read_result_event(
    session,
    screenshot_id: uuid.UUID,
    analysis_id: uuid.UUID | None = None,
) -> screenshot_pb2.RunAnalysisEvent:
    """Читает финальный результат из БД и возвращает готовый RunAnalysisEvent."""
    screenshot_row = await session.get(Screenshot, screenshot_id)
    if analysis_id:
        analysis_row = await session.get(Analysis, analysis_id)
    else:
        result = await session.execute(
            select(Analysis)
            .where(Analysis.screenshot_id == screenshot_id)
            .order_by(desc(Analysis.created_at))
            .limit(1)
        )
        analysis_row = result.scalar_one_or_none()

    if not screenshot_row or not analysis_row:
        return screenshot_pb2.RunAnalysisEvent(
            failed=screenshot_pb2.RunAnalysisFailedEvent(error_message="Результат анализа не найден в БД")
        )

    if screenshot_row.status == ScreenshotStatus.completed:
        return screenshot_pb2.RunAnalysisEvent(
            completed=screenshot_pb2.RunAnalysisCompletedEvent(
                analysis=_analysis_to_proto(analysis_row),
                screenshot=_screenshot_to_proto(screenshot_row),
            )
        )

    error_msg = analysis_row.error_message or "Анализ завершился с ошибкой"
    return screenshot_pb2.RunAnalysisEvent(
        failed=screenshot_pb2.RunAnalysisFailedEvent(error_message=error_msg)
    )


async def _run_analysis_and_notify(
    screenshot_id: uuid.UUID,
    analysis_id: uuid.UUID,
    model_name: str,
    storage_bucket: str,
    storage_key: str,
) -> None:
    """Запускает анализ и по завершении (успех или ошибка) взводит asyncio.Event."""
    try:
        await _run_analysis(screenshot_id, analysis_id, model_name, storage_bucket, storage_key)
    finally:
        event = _analysis_done.pop(screenshot_id, None)
        if event:
            event.set()


async def _run_analysis(
    screenshot_id: uuid.UUID,
    analysis_id: uuid.UUID,
    model_name: str,
    storage_bucket: str,
    storage_key: str,
) -> None:
    """Фоновая задача: вызывает сервис анализа и сохраняет результат."""
    try:
        response = await analyzer_client.analyze_screenshot(
            screenshot_id=str(screenshot_id),
            storage_bucket=storage_bucket,
            storage_key=storage_key,
            model_name=model_name,
        )
    except Exception as exc:
        logger.exception("Analyzer RPC failed for screenshot %s: %s", screenshot_id, exc)
        await _mark_analysis_failed(analysis_id, screenshot_id, str(exc))
        return

    if not response.success:
        await _mark_analysis_failed(analysis_id, screenshot_id, response.error_message)
        return

    result_json = {
        "screen_type": response.screen_type,
        "summary": response.summary,
        "sections": [
            {"name": s.name, "description": s.description}
            for s in response.sections
        ],
        "ui_issues": [
            {
                "title": i.title,
                "severity": i.severity,
                "description": i.description,
                "evidence": i.evidence,
                "recommendation": i.recommendation,
            }
            for i in response.ui_issues
        ],
        "ux_suggestions": [
            {"title": s.title, "description": s.description}
            for s in response.ux_suggestions
        ],
        "implementation_tasks": [
            {"title": t.title, "description": t.description, "priority": t.priority}
            for t in response.implementation_tasks
        ],
    }

    async with AsyncSessionLocal() as session:
        analysis = await session.get(Analysis, analysis_id)
        screenshot = await session.get(Screenshot, screenshot_id)
        if analysis and screenshot:
            analysis.summary = response.summary
            analysis.result_json = result_json
            analysis.error_message = None
            screenshot.status = ScreenshotStatus.completed
            await session.commit()
            logger.info("Analysis %s completed for screenshot %s", analysis_id, screenshot_id)


async def _mark_analysis_failed(
    analysis_id: uuid.UUID,
    screenshot_id: uuid.UUID,
    error_message: str,
) -> None:
    async with AsyncSessionLocal() as session:
        analysis = await session.get(Analysis, analysis_id)
        screenshot = await session.get(Screenshot, screenshot_id)
        if analysis and screenshot:
            analysis.error_message = error_message
            screenshot.status = ScreenshotStatus.failed
            await session.commit()
