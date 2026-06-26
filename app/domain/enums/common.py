from enum import Enum


class SourceType(str, Enum):
    API = "API"
    RSS = "RSS"
    BLOG = "BLOG"
    WEB = "WEB"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
