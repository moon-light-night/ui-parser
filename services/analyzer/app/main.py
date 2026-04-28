from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.grpc_server import start_grpc_server


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        grpc_server = await start_grpc_server()
        application.state.grpc_server = grpc_server
        try:
            yield
        finally:
            await grpc_server.stop(grace=3)

    application = FastAPI(
        title="UI Screenshot Analyzer - Analyzer",
        description="Internal analyzer service",
        version="0.1.0",
        lifespan=lifespan,
    )

    @application.get("/")
    async def root() -> dict[str, str]:
        return {"service": "analyzer", "status": "ok"}

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()
