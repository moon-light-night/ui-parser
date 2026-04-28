from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("healthy", "version", "services")
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    version: str
    services: _containers.RepeatedCompositeFieldContainer[ServiceStatus]
    def __init__(self, healthy: bool = ..., version: _Optional[str] = ..., services: _Optional[_Iterable[_Union[ServiceStatus, _Mapping]]] = ...) -> None: ...

class ServiceStatus(_message.Message):
    __slots__ = ("name", "healthy", "message")
    NAME_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    healthy: bool
    message: str
    def __init__(self, name: _Optional[str] = ..., healthy: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetInfoResponse(_message.Message):
    __slots__ = ("version", "environment", "available_models")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_MODELS_FIELD_NUMBER: _ClassVar[int]
    version: str
    environment: str
    available_models: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, version: _Optional[str] = ..., environment: _Optional[str] = ..., available_models: _Optional[_Iterable[str]] = ...) -> None: ...
