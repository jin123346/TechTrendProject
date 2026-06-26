from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ErrorResponse(BaseModel):
    error_code: str
    message: str


def clamp_page_size(page_size: int, max_page_size: int = 100) -> int:
    return min(max(page_size, 1), max_page_size)
