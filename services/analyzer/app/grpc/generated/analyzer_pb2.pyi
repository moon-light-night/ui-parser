from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzeScreenshotRequest(_message.Message):
    __slots__ = ("screenshot_id", "storage_bucket", "storage_key", "image_data", "model_name", "analysis_mode")
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUCKET_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_MODE_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    storage_bucket: str
    storage_key: str
    image_data: bytes
    model_name: str
    analysis_mode: str
    def __init__(self, screenshot_id: _Optional[str] = ..., storage_bucket: _Optional[str] = ..., storage_key: _Optional[str] = ..., image_data: _Optional[bytes] = ..., model_name: _Optional[str] = ..., analysis_mode: _Optional[str] = ...) -> None: ...

class AnalyzeScreenshotResponse(_message.Message):
    __slots__ = ("analysis_id", "screen_type", "summary", "sections", "ui_issues", "ux_suggestions", "implementation_tasks", "raw_json", "error_message", "success")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    SCREEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    UI_ISSUES_FIELD_NUMBER: _ClassVar[int]
    UX_SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_TASKS_FIELD_NUMBER: _ClassVar[int]
    RAW_JSON_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    screen_type: str
    summary: str
    sections: _containers.RepeatedCompositeFieldContainer[Section]
    ui_issues: _containers.RepeatedCompositeFieldContainer[Issue]
    ux_suggestions: _containers.RepeatedCompositeFieldContainer[Suggestion]
    implementation_tasks: _containers.RepeatedCompositeFieldContainer[Task]
    raw_json: str
    error_message: str
    success: bool
    def __init__(self, analysis_id: _Optional[str] = ..., screen_type: _Optional[str] = ..., summary: _Optional[str] = ..., sections: _Optional[_Iterable[_Union[Section, _Mapping]]] = ..., ui_issues: _Optional[_Iterable[_Union[Issue, _Mapping]]] = ..., ux_suggestions: _Optional[_Iterable[_Union[Suggestion, _Mapping]]] = ..., implementation_tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., raw_json: _Optional[str] = ..., error_message: _Optional[str] = ..., success: bool = ...) -> None: ...

class Section(_message.Message):
    __slots__ = ("name", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Issue(_message.Message):
    __slots__ = ("title", "severity", "description", "evidence", "recommendation")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    title: str
    severity: str
    description: str
    evidence: str
    recommendation: str
    def __init__(self, title: _Optional[str] = ..., severity: _Optional[str] = ..., description: _Optional[str] = ..., evidence: _Optional[str] = ..., recommendation: _Optional[str] = ...) -> None: ...

class Suggestion(_message.Message):
    __slots__ = ("title", "description")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("title", "description", "priority")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    priority: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., priority: _Optional[str] = ...) -> None: ...

class GenerateChatReplyRequest(_message.Message):
    __slots__ = ("session_id", "screenshot_id", "screenshot_context", "analysis_context", "history", "user_message", "model_name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    USER_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    screenshot_id: str
    screenshot_context: ScreenshotContext
    analysis_context: AnalysisContext
    history: _containers.RepeatedCompositeFieldContainer[ConversationMessage]
    user_message: str
    model_name: str
    def __init__(self, session_id: _Optional[str] = ..., screenshot_id: _Optional[str] = ..., screenshot_context: _Optional[_Union[ScreenshotContext, _Mapping]] = ..., analysis_context: _Optional[_Union[AnalysisContext, _Mapping]] = ..., history: _Optional[_Iterable[_Union[ConversationMessage, _Mapping]]] = ..., user_message: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class ScreenshotContext(_message.Message):
    __slots__ = ("original_filename", "mime_type", "storage_bucket", "storage_key", "image_data")
    ORIGINAL_FILENAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUCKET_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    original_filename: str
    mime_type: str
    storage_bucket: str
    storage_key: str
    image_data: bytes
    def __init__(self, original_filename: _Optional[str] = ..., mime_type: _Optional[str] = ..., storage_bucket: _Optional[str] = ..., storage_key: _Optional[str] = ..., image_data: _Optional[bytes] = ...) -> None: ...

class AnalysisContext(_message.Message):
    __slots__ = ("screen_type", "summary", "analysis_json")
    SCREEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_JSON_FIELD_NUMBER: _ClassVar[int]
    screen_type: str
    summary: str
    analysis_json: str
    def __init__(self, screen_type: _Optional[str] = ..., summary: _Optional[str] = ..., analysis_json: _Optional[str] = ...) -> None: ...

class ConversationMessage(_message.Message):
    __slots__ = ("role", "content")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    def __init__(self, role: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class GenerateChatReplyEvent(_message.Message):
    __slots__ = ("chunk", "done", "error")
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    chunk: ChunkEvent
    done: DoneEvent
    error: ErrorEvent
    def __init__(self, chunk: _Optional[_Union[ChunkEvent, _Mapping]] = ..., done: _Optional[_Union[DoneEvent, _Mapping]] = ..., error: _Optional[_Union[ErrorEvent, _Mapping]] = ...) -> None: ...

class ChunkEvent(_message.Message):
    __slots__ = ("text", "index")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    text: str
    index: int
    def __init__(self, text: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...

class DoneEvent(_message.Message):
    __slots__ = ("full_response", "model_name", "total_tokens")
    FULL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    full_response: str
    model_name: str
    total_tokens: int
    def __init__(self, full_response: _Optional[str] = ..., model_name: _Optional[str] = ..., total_tokens: _Optional[int] = ...) -> None: ...

class ErrorEvent(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class GenerateTitleRequest(_message.Message):
    __slots__ = ("user_message", "model_name")
    USER_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    user_message: str
    model_name: str
    def __init__(self, user_message: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class GenerateTitleResponse(_message.Message):
    __slots__ = ("title", "success", "error_message")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    title: str
    success: bool
    error_message: str
    def __init__(self, title: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...
