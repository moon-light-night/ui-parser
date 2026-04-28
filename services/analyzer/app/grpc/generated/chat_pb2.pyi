import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatSession(_message.Message):
    __slots__ = ("id", "screenshot_id", "title", "message_count", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    screenshot_id: str
    title: str
    message_count: int
    created_at: _common_pb2.Timestamp
    updated_at: _common_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., screenshot_id: _Optional[str] = ..., title: _Optional[str] = ..., message_count: _Optional[int] = ..., created_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("id", "session_id", "role", "content", "status", "model_name", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    session_id: str
    role: _common_pb2.MessageRole
    content: str
    status: _common_pb2.MessageStatus
    model_name: str
    created_at: _common_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., session_id: _Optional[str] = ..., role: _Optional[_Union[_common_pb2.MessageRole, str]] = ..., content: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.MessageStatus, str]] = ..., model_name: _Optional[str] = ..., created_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateSessionRequest(_message.Message):
    __slots__ = ("screenshot_id", "title")
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    title: str
    def __init__(self, screenshot_id: _Optional[str] = ..., title: _Optional[str] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: ChatSession
    def __init__(self, session: _Optional[_Union[ChatSession, _Mapping]] = ...) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ("screenshot_id", "pagination")
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    pagination: _common_pb2.PaginationRequest
    def __init__(self, screenshot_id: _Optional[str] = ..., pagination: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class ListSessionsResponse(_message.Message):
    __slots__ = ("sessions", "pagination")
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[ChatSession]
    pagination: _common_pb2.PaginationResponse
    def __init__(self, sessions: _Optional[_Iterable[_Union[ChatSession, _Mapping]]] = ..., pagination: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetSessionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class GetSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: ChatSession
    def __init__(self, session: _Optional[_Union[ChatSession, _Mapping]] = ...) -> None: ...

class DeleteSessionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class DeleteSessionResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListMessagesRequest(_message.Message):
    __slots__ = ("session_id", "pagination")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pagination: _common_pb2.PaginationRequest
    def __init__(self, session_id: _Optional[str] = ..., pagination: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class ListMessagesResponse(_message.Message):
    __slots__ = ("messages", "pagination")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    pagination: _common_pb2.PaginationResponse
    def __init__(self, messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., pagination: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class SendMessageRequest(_message.Message):
    __slots__ = ("session_id", "content")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    content: str
    def __init__(self, session_id: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class SendMessageEvent(_message.Message):
    __slots__ = ("message_created", "assistant_chunk", "assistant_done", "error")
    MESSAGE_CREATED_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_CHUNK_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_DONE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message_created: MessageCreatedEvent
    assistant_chunk: AssistantChunkEvent
    assistant_done: AssistantDoneEvent
    error: ErrorEvent
    def __init__(self, message_created: _Optional[_Union[MessageCreatedEvent, _Mapping]] = ..., assistant_chunk: _Optional[_Union[AssistantChunkEvent, _Mapping]] = ..., assistant_done: _Optional[_Union[AssistantDoneEvent, _Mapping]] = ..., error: _Optional[_Union[ErrorEvent, _Mapping]] = ...) -> None: ...

class MessageCreatedEvent(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: ChatMessage
    def __init__(self, message: _Optional[_Union[ChatMessage, _Mapping]] = ...) -> None: ...

class AssistantChunkEvent(_message.Message):
    __slots__ = ("chunk", "index")
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    chunk: str
    index: int
    def __init__(self, chunk: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...

class AssistantDoneEvent(_message.Message):
    __slots__ = ("message", "new_session_title")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_SESSION_TITLE_FIELD_NUMBER: _ClassVar[int]
    message: ChatMessage
    new_session_title: str
    def __init__(self, message: _Optional[_Union[ChatMessage, _Mapping]] = ..., new_session_title: _Optional[str] = ...) -> None: ...

class ErrorEvent(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ResumeMessageStreamRequest(_message.Message):
    __slots__ = ("message_id",)
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    def __init__(self, message_id: _Optional[str] = ...) -> None: ...
