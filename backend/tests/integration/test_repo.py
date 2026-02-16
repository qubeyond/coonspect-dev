from datetime import datetime

import pytest
from dishka import AsyncContainer

from app.domain.entities.lecture import Lecture, LectureStatus
from app.domain.entities.value_objects import (
    AuthorId,
    LectureId,
    Tag,
    Title,
)
from app.domain.interfaces.lecture_repo import ILectureRepository


@pytest.mark.asyncio
async def test_lecture_repo_lifecycle(container: AsyncContainer):
    # Входим в Scope.REQUEST, так как репозиторий живет там
    async with container() as request_container:
        repo = await request_container.get(ILectureRepository)
        now = datetime.now()

        # 1. ADD
        lecture = Lecture(
            author_id=AuthorId("user_123"),
            title=Title("Clean Architecture в 2026"),
            tags=frozenset([Tag("python"), Tag("architecture")]),
            registered_at=now,
            updated_at=now,
        )

        lecture_id = await repo.add(lecture)
        assert isinstance(lecture_id, LectureId)

        # 2. FIND
        fetched = await repo.find_by_id(lecture_id)
        assert fetched is not None
        assert fetched.title.value == "Clean Architecture в 2026"
        assert Tag("python") in fetched.tags

        # 3. SAVE (Update status)
        fetched.start_processing(at=datetime.now())
        await repo.save(fetched)

        after_processing = await repo.find_by_id(lecture_id)
        assert after_processing.status == LectureStatus.PROCESSING

        # 4. DELETE
        deleted = await repo.delete(lecture_id)
        assert deleted is True
        assert await repo.find_by_id(lecture_id) is None


@pytest.mark.asyncio
async def test_find_all_with_filters(container: AsyncContainer):
    async with container() as request_container:
        repo = await request_container.get(ILectureRepository)
        author = AuthorId("author_pagination_test")
        now = datetime.now()

        # Создаем тестовые данные
        for i in range(5):
            lecture_item = Lecture(
                author_id=author,
                title=Title(f"L {i}"),
                registered_at=now,
                updated_at=now,
            )
            await repo.add(lecture_item)

        # Проверяем фильтрацию и лимиты
        results = await repo.find_all(author_id=author, limit=3, offset=0)
        assert len(results) == 3

        total = await repo.count(author_id=author)
        assert total >= 5
