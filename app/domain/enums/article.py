from enum import Enum


class ArticleFetchStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    FETCH_PENDING = "FETCH_PENDING"
    FETCHING = "FETCHING"
    FETCHED = "FETCHED"
    FETCH_FAILED = "FETCH_FAILED"
