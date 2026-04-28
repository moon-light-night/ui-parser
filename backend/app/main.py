from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app.grpc.server import start_grpc_server
from app.models.db import Base
from app.storage import ensure_bucket_exists

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        try:
            ensure_bucket_exists()
        except Exception as exc:
            logger.warning("Could not ensure S3 bucket: %s", exc)

        grpc_server = await start_grpc_server()
        application.state.grpc_server = grpc_server
        try:
            yield
        finally:
            await grpc_server.stop(grace=3)
            await engine.dispose()

    application = FastAPI(
        title="UI Parser API",
        description="UI Screenshot Analyzer — backend API",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok", "service": "ui-parser-api"}

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()
