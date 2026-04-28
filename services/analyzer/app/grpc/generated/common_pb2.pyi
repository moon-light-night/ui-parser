from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ScreenshotStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCREENSHOT_STATUS_UNSPECIFIED: _ClassVar[ScreenshotStatus]
    SCREENSHOT_STATUS_UPLOADED: _ClassVar[ScreenshotStatus]
    SCREENSHOT_STATUS_ANALYZING: _ClassVar[ScreenshotStatus]
    SCREENSHOT_STATUS_COMPLETED: _ClassVar[ScreenshotStatus]
    SCREENSHOT_STATUS_FAILED: _ClassVar[ScreenshotStatus]

class MessageRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGE_ROLE_UNSPECIFIED: _ClassVar[MessageRole]
    MESSAGE_ROLE_USER: _ClassVar[MessageRole]
    MESSAGE_ROLE_ASSISTANT: _ClassVar[MessageRole]
    MESSAGE_ROLE_SYSTEM: _ClassVar[MessageRole]

class MessageStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGE_STATUS_UNSPECIFIED: _ClassVar[MessageStatus]
    MESSAGE_STATUS_COMPLETED: _ClassVar[MessageStatus]
    MESSAGE_STATUS_STREAMING: _ClassVar[MessageStatus]
    MESSAGE_STATUS_FAILED: _ClassVar[MessageStatus]

class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEVERITY_UNSPECIFIED: _ClassVar[Severity]
    SEVERITY_LOW: _ClassVar[Severity]
    SEVERITY_MEDIUM: _ClassVar[Severity]
    SEVERITY_HIGH: _ClassVar[Severity]

class Priority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRIORITY_UNSPECIFIED: _ClassVar[Priority]
    PRIORITY_LOW: _ClassVar[Priority]
    PRIORITY_MEDIUM: _ClassVar[Priority]
    PRIORITY_HIGH: _ClassVar[Priority]
SCREENSHOT_STATUS_UNSPECIFIED: ScreenshotStatus
SCREENSHOT_STATUS_UPLOADED: ScreenshotStatus
SCREENSHOT_STATUS_ANALYZING: ScreenshotStatus
SCREENSHOT_STATUS_COMPLETED: ScreenshotStatus
SCREENSHOT_STATUS_FAILED: ScreenshotStatus
MESSAGE_ROLE_UNSPECIFIED: MessageRole
MESSAGE_ROLE_USER: MessageRole
MESSAGE_ROLE_ASSISTANT: MessageRole
MESSAGE_ROLE_SYSTEM: MessageRole
MESSAGE_STATUS_UNSPECIFIED: MessageStatus
MESSAGE_STATUS_COMPLETED: MessageStatus
MESSAGE_STATUS_STREAMING: MessageStatus
MESSAGE_STATUS_FAILED: MessageStatus
SEVERITY_UNSPECIFIED: Severity
SEVERITY_LOW: Severity
SEVERITY_MEDIUM: Severity
SEVERITY_HIGH: Severity
PRIORITY_UNSPECIFIED: Priority
PRIORITY_LOW: Priority
PRIORITY_MEDIUM: Priority
PRIORITY_HIGH: Priority

class Timestamp(_message.Message):
    __slots__ = ("seconds", "nanos")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    NANOS_FIELD_NUMBER: _ClassVar[int]
    seconds: int
    nanos: int
    def __init__(self, seconds: _Optional[int] = ..., nanos: _Optional[int] = ...) -> None: ...

class PaginationRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ("next_page_token", "total_count")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    total_count: int
    def __init__(self, next_page_token: _Optional[str] = ..., total_count: _Optional[int] = ...) -> None: ...
