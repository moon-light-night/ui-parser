import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Screenshot(_message.Message):
    __slots__ = ("id", "title", "original_filename", "mime_type", "file_size", "storage_bucket", "storage_key", "storage_region", "storage_url", "status", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_FILENAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUCKET_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    STORAGE_REGION_FIELD_NUMBER: _ClassVar[int]
    STORAGE_URL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    original_filename: str
    mime_type: str
    file_size: int
    storage_bucket: str
    storage_key: str
    storage_region: str
    storage_url: str
    status: _common_pb2.ScreenshotStatus
    created_at: _common_pb2.Timestamp
    updated_at: _common_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., original_filename: _Optional[str] = ..., mime_type: _Optional[str] = ..., file_size: _Optional[int] = ..., storage_bucket: _Optional[str] = ..., storage_key: _Optional[str] = ..., storage_region: _Optional[str] = ..., storage_url: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.ScreenshotStatus, str]] = ..., created_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AnalysisSection(_message.Message):
    __slots__ = ("name", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class UiIssue(_message.Message):
    __slots__ = ("title", "severity", "description", "evidence", "recommendation")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    title: str
    severity: _common_pb2.Severity
    description: str
    evidence: str
    recommendation: str
    def __init__(self, title: _Optional[str] = ..., severity: _Optional[_Union[_common_pb2.Severity, str]] = ..., description: _Optional[str] = ..., evidence: _Optional[str] = ..., recommendation: _Optional[str] = ...) -> None: ...

class UxSuggestion(_message.Message):
    __slots__ = ("title", "description")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ImplementationTask(_message.Message):
    __slots__ = ("title", "description", "priority")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    priority: _common_pb2.Priority
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., priority: _Optional[_Union[_common_pb2.Priority, str]] = ...) -> None: ...

class Analysis(_message.Message):
    __slots__ = ("id", "screenshot_id", "model_name", "screen_type", "summary", "sections", "ui_issues", "ux_suggestions", "implementation_tasks", "error_message", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    SCREEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    UI_ISSUES_FIELD_NUMBER: _ClassVar[int]
    UX_SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_TASKS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    screenshot_id: str
    model_name: str
    screen_type: str
    summary: str
    sections: _containers.RepeatedCompositeFieldContainer[AnalysisSection]
    ui_issues: _containers.RepeatedCompositeFieldContainer[UiIssue]
    ux_suggestions: _containers.RepeatedCompositeFieldContainer[UxSuggestion]
    implementation_tasks: _containers.RepeatedCompositeFieldContainer[ImplementationTask]
    error_message: str
    created_at: _common_pb2.Timestamp
    updated_at: _common_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., screenshot_id: _Optional[str] = ..., model_name: _Optional[str] = ..., screen_type: _Optional[str] = ..., summary: _Optional[str] = ..., sections: _Optional[_Iterable[_Union[AnalysisSection, _Mapping]]] = ..., ui_issues: _Optional[_Iterable[_Union[UiIssue, _Mapping]]] = ..., ux_suggestions: _Optional[_Iterable[_Union[UxSuggestion, _Mapping]]] = ..., implementation_tasks: _Optional[_Iterable[_Union[ImplementationTask, _Mapping]]] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_common_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateUploadUrlRequest(_message.Message):
    __slots__ = ("filename", "mime_type", "file_size")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    filename: str
    mime_type: str
    file_size: int
    def __init__(self, filename: _Optional[str] = ..., mime_type: _Optional[str] = ..., file_size: _Optional[int] = ...) -> None: ...

class CreateUploadUrlResponse(_message.Message):
    __slots__ = ("upload_url", "storage_bucket", "storage_key", "expires_at")
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUCKET_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    storage_bucket: str
    storage_key: str
    expires_at: int
    def __init__(self, upload_url: _Optional[str] = ..., storage_bucket: _Optional[str] = ..., storage_key: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

class RegisterScreenshotRequest(_message.Message):
    __slots__ = ("original_filename", "mime_type", "file_size", "storage_bucket", "storage_key", "title")
    ORIGINAL_FILENAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUCKET_FIELD_NUMBER: _ClassVar[int]
    STORAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    original_filename: str
    mime_type: str
    file_size: int
    storage_bucket: str
    storage_key: str
    title: str
    def __init__(self, original_filename: _Optional[str] = ..., mime_type: _Optional[str] = ..., file_size: _Optional[int] = ..., storage_bucket: _Optional[str] = ..., storage_key: _Optional[str] = ..., title: _Optional[str] = ...) -> None: ...

class RegisterScreenshotResponse(_message.Message):
    __slots__ = ("screenshot",)
    SCREENSHOT_FIELD_NUMBER: _ClassVar[int]
    screenshot: Screenshot
    def __init__(self, screenshot: _Optional[_Union[Screenshot, _Mapping]] = ...) -> None: ...

class ListScreenshotsRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: _common_pb2.PaginationRequest
    def __init__(self, pagination: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class ListScreenshotsResponse(_message.Message):
    __slots__ = ("screenshots", "pagination")
    SCREENSHOTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    screenshots: _containers.RepeatedCompositeFieldContainer[Screenshot]
    pagination: _common_pb2.PaginationResponse
    def __init__(self, screenshots: _Optional[_Iterable[_Union[Screenshot, _Mapping]]] = ..., pagination: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetScreenshotRequest(_message.Message):
    __slots__ = ("screenshot_id",)
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    def __init__(self, screenshot_id: _Optional[str] = ...) -> None: ...

class GetScreenshotResponse(_message.Message):
    __slots__ = ("screenshot",)
    SCREENSHOT_FIELD_NUMBER: _ClassVar[int]
    screenshot: Screenshot
    def __init__(self, screenshot: _Optional[_Union[Screenshot, _Mapping]] = ...) -> None: ...

class StartAnalysisRequest(_message.Message):
    __slots__ = ("screenshot_id", "model_name")
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    model_name: str
    def __init__(self, screenshot_id: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class StartAnalysisResponse(_message.Message):
    __slots__ = ("analysis_id", "status")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    status: _common_pb2.ScreenshotStatus
    def __init__(self, analysis_id: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.ScreenshotStatus, str]] = ...) -> None: ...

class GetLatestAnalysisRequest(_message.Message):
    __slots__ = ("screenshot_id",)
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    def __init__(self, screenshot_id: _Optional[str] = ...) -> None: ...

class GetLatestAnalysisResponse(_message.Message):
    __slots__ = ("analysis",)
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    analysis: Analysis
    def __init__(self, analysis: _Optional[_Union[Analysis, _Mapping]] = ...) -> None: ...

class RunAnalysisRequest(_message.Message):
    __slots__ = ("screenshot_id", "model_name")
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    model_name: str
    def __init__(self, screenshot_id: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class RunAnalysisEvent(_message.Message):
    __slots__ = ("started", "completed", "failed")
    STARTED_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    started: RunAnalysisStartedEvent
    completed: RunAnalysisCompletedEvent
    failed: RunAnalysisFailedEvent
    def __init__(self, started: _Optional[_Union[RunAnalysisStartedEvent, _Mapping]] = ..., completed: _Optional[_Union[RunAnalysisCompletedEvent, _Mapping]] = ..., failed: _Optional[_Union[RunAnalysisFailedEvent, _Mapping]] = ...) -> None: ...

class RunAnalysisStartedEvent(_message.Message):
    __slots__ = ("analysis_id",)
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    def __init__(self, analysis_id: _Optional[str] = ...) -> None: ...

class RunAnalysisCompletedEvent(_message.Message):
    __slots__ = ("analysis", "screenshot")
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_FIELD_NUMBER: _ClassVar[int]
    analysis: Analysis
    screenshot: Screenshot
    def __init__(self, analysis: _Optional[_Union[Analysis, _Mapping]] = ..., screenshot: _Optional[_Union[Screenshot, _Mapping]] = ...) -> None: ...

class RunAnalysisFailedEvent(_message.Message):
    __slots__ = ("error_message",)
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    def __init__(self, error_message: _Optional[str] = ...) -> None: ...

class DeleteScreenshotRequest(_message.Message):
    __slots__ = ("screenshot_id",)
    SCREENSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    screenshot_id: str
    def __init__(self, screenshot_id: _Optional[str] = ...) -> None: ...

class DeleteScreenshotResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
