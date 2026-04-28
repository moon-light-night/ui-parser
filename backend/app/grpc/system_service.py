"""Реализация gRPC SystemService."""
from __future__ import annotations

import grpc

from .generated import system_pb2, system_pb2_grpc

_VERSION = "0.1.0"


class SystemServicer(system_pb2_grpc.SystemServiceServicer):

    async def Health(
        self,
        request: system_pb2.HealthRequest,
        context: grpc.aio.ServicerContext,
    ) -> system_pb2.HealthResponse:
        return system_pb2.HealthResponse(
            healthy=True,
            version=_VERSION,
            services=[
                system_pb2.ServiceStatus(name="api", healthy=True, message="ok"),
            ],
        )

    async def GetInfo(
        self,
        request: system_pb2.GetInfoRequest,
        context: grpc.aio.ServicerContext,
    ) -> system_pb2.GetInfoResponse:
        return system_pb2.GetInfoResponse(
            version=_VERSION,
            environment="local",
            available_models=["gemma4:31b-cloud"],
        )
