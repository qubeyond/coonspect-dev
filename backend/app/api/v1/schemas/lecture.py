from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.entities.lecture import LectureStatus


class TranscriptSchema(BaseModel):
    text: str
    language: str | None = None
    confidence: float | None = None


class LectureBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    tags: list[str] = Field(default_factory=list)


class LectureCreate(LectureBase):
    author_id: str


class LectureUpdate(BaseModel):
    title: str | None = None
    tags: list[str] | None = None


class LectureRead(LectureBase):
    id: str
    author_id: str
    status: LectureStatus
    content: TranscriptSchema | None = None
    registered_at: datetime
    updated_at: datetime
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def transform_domain_to_schema(cls, data: Any) -> Any:
        if not isinstance(data, dict) and hasattr(data, "id"):

            def extract(obj: Any) -> Any:
                return obj.value if hasattr(obj, "value") else obj

            return {
                "id": extract(data.id),
                "author_id": extract(data.author_id),
                "title": extract(data.title),
                "tags": [extract(t) for t in data.tags]
                if hasattr(data, "tags")
                else [],
                "status": data.status,
                "registered_at": data.registered_at,
                "updated_at": data.updated_at,
                "published_at": getattr(data, "published_at", None),
                "content": getattr(data, "content", None),
            }
        return data
