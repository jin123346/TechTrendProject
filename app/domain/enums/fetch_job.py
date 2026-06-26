from enum import Enum


class FetchJobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class FetchRequestType(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    RETRY = "RETRY"
    REFRESH = "REFRESH"
