from datetime import datetime

import pytest

from app.domain.entities.lecture import Lecture, LectureStatus
from app.domain.entities.value_objects import AuthorId, Title
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.tasks.lecture import process_lecture_task


@pytest.mark.asyncio
async def test_process_lecture_task_logic(container):
    # Входим в request scope (тот же, в котором живет repo)
    async with container() as request_container:
        # 1. Получаем репо, чтобы подготовить данные для теста
        repo = await request_container.get(ILectureRepository)

        lecture = Lecture(
            author_id=AuthorId("task_user"),
            title=Title("Task Coverage Test"),
            registered_at=datetime.now(),
            updated_at=datetime.now(),
        )
        l_id = await repo.add(lecture)

        # 2. Вызываем задачу.
        # Мы НЕ передаем repo вручную. Мы передаем только dishka_container.
        # Декоратор @inject сам возьмет repo из этого контейнера.
        await process_lecture_task(
            lecture_id=str(l_id.value), dishka_container=request_container
        )

        # 3. Проверяем, что логика внутри (status, complete) отработала
        updated = await repo.find_by_id(l_id)
        assert updated is not None
        assert updated.status == LectureStatus.COMPLETED
        assert "расшифровка" in updated.content.text
