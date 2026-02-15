from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class LectureBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: dict[str, Any]
    tags: list[str] = Field(default_factory=list)


class LectureCreate(LectureBase):
    author_id: str | None = None


class LectureUpdate(BaseModel):
    title: str | None = None
    content: dict[str, Any] | None = None
    tags: list[str] | None = None


class LectureRead(LectureBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True