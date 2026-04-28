from __future__ import annotations

import os

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from app.analyzer_service import AnalyzerServicer
from app.grpc.generated import analyzer_pb2_grpc


async def start_grpc_server() -> grpc.aio.Server:
    grpc_host = os.getenv("ANALYZER_GRPC_HOST", "0.0.0.0")
    grpc_port = int(os.getenv("ANALYZER_GRPC_PORT", "50061"))

    server = grpc.aio.server()

    # Регистрируем сервис анализатора
    analyzer_pb2_grpc.add_AnalyzerServiceServicer_to_server(AnalyzerServicer(), server)

    # Регистрируем gRPC health-протокол
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("uiparser.analyzer.AnalyzerService", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f"{grpc_host}:{grpc_port}")
    await server.start()
    return server
