from enum import Enum


class PipelineRequestType(str, Enum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    RETRY = "RETRY"
    API = "API"


class PipelineRequestStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PipelineRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
