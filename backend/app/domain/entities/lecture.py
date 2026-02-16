from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.entities.value_objects import (
    AuthorId,
    InvalidStateTransitionError,
    LectureId,
    Tag,
    Title,
    Transcript,
)


class LectureStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(kw_only=True)
class Lecture:
    id: LectureId | None = None
    author_id: AuthorId

    title: Title
    content: Transcript | None = None
    tags: frozenset[Tag] = field(default_factory=frozenset)

    status: LectureStatus = LectureStatus.PENDING

    registered_at: datetime
    updated_at: datetime
    published_at: datetime | None = None

    def start_processing(self, at: datetime) -> None:
        if self.status not in (LectureStatus.PENDING, LectureStatus.FAILED):
            raise InvalidStateTransitionError(
                f"Cannot start processing from {self.status}"
            )

        self.status = LectureStatus.PROCESSING
        self.updated_at = at

    def complete(self, transcript: Transcript, at: datetime) -> None:
        """Принимаем объект Transcript, а не dict"""
        if self.status != LectureStatus.PROCESSING:
            raise InvalidStateTransitionError(
                "Can only complete from processing status"
            )

        self.content = transcript
        self.status = LectureStatus.COMPLETED
        self.published_at = at
        self.updated_at = at

    def fail(self, at: datetime) -> None:
        self.status = LectureStatus.FAILED
        self.updated_at = at

    def update_info(
        self,
        at: datetime,
        title: Title | None = None,
        tags: frozenset[Tag] | None = None,
    ) -> None:
        """Обновляем метаданные, используя строгие типы"""
        if title:
            self.title = title
        if tags is not None:
            self.tags = tags
        self.updated_at = at
