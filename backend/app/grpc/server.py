from __future__ import annotations

import os

import grpc

from .generated import chat_pb2_grpc, screenshot_pb2_grpc, system_pb2_grpc
from .chat_service import ChatServicer
from .screenshot_service import ScreenshotServicer
from .system_service import SystemServicer


async def start_grpc_server() -> grpc.aio.Server:
    grpc_host = os.getenv("GRPC_HOST", "0.0.0.0")
    grpc_port = int(os.getenv("GRPC_PORT", "50051"))

    server = grpc.aio.server()
    screenshot_pb2_grpc.add_ScreenshotServiceServicer_to_server(ScreenshotServicer(), server)
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    system_pb2_grpc.add_SystemServiceServicer_to_server(SystemServicer(), server)

    server.add_insecure_port(f"{grpc_host}:{grpc_port}")
    await server.start()
    return server

