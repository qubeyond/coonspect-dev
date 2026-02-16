from datetime import datetime

import pytest

from app.domain.entities.lecture import (
    InvalidStateTransitionError,
    Lecture,
    LectureStatus,
)
from app.domain.entities.value_objects import (
    AuthorId,
    Tag,
    Title,
    Transcript,
)


def test_lecture_creation_and_validation():
    now = datetime.now()
    lecture = Lecture(
        author_id=AuthorId("auth_1"),
        title=Title("Valid Title"),
        registered_at=now,
        updated_at=now,
    )
    assert lecture.status == LectureStatus.PENDING
    assert lecture.title.value == "Valid Title"

    with pytest.raises(ValueError):
        Title("")


def test_lecture_status_transitions():
    now = datetime.now()
    lecture = Lecture(
        author_id=AuthorId("1"), title=Title("Test"), registered_at=now, updated_at=now
    )

    lecture.start_processing(at=now)
    assert lecture.status == LectureStatus.PROCESSING

    lecture.status = LectureStatus.PENDING
    with pytest.raises(InvalidStateTransitionError):
        lecture.complete(Transcript(text="hi"), at=now)


def test_tag_normalization():
    tag = Tag("  PyThOn  ")
    assert tag.value == "python"
