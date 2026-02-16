import asyncio
from datetime import datetime

from dishka.integrations.taskiq import FromDishka, inject

from app.domain.entities.value_objects import LectureId, Transcript
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.infra.taskiq.broker import broker


@broker.task
@inject
async def process_lecture_task(
    lecture_id: str, repo: FromDishka[ILectureRepository]
) -> None:
    lecture = await repo.find_by_id(LectureId(lecture_id))
    if not lecture:
        return

    lecture.start_processing(at=datetime.now())
    await repo.save(lecture)

    await asyncio.sleep(10)

    mock_transcript = Transcript(
        text="Это тестовая расшифровка лекции", language="ru", confidence=0.99
    )

    lecture.complete(transcript=mock_transcript, at=datetime.now())
    await repo.save(lecture)
