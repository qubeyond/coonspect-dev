from datetime import datetime
from typing import Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.lecture import LectureCreate, LectureRead, LectureUpdate
from app.domain.entities.lecture import Lecture
from app.domain.entities.value_objects import (
    AuthorId,
    LectureId,
    Tag,
    Title,
)
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.tasks.lecture import process_lecture_task

router = APIRouter()


@router.post("/", response_model=LectureRead, status_code=status.HTTP_201_CREATED)
@inject
async def create_lecture(
    data: LectureCreate, repo: FromDishka[ILectureRepository]
) -> Any:
    now = datetime.now()

    new_lecture = Lecture(
        author_id=AuthorId(data.author_id),
        title=Title(data.title),
        content=None,
        tags=frozenset(Tag(t) for t in data.tags),
        registered_at=now,
        updated_at=now,
    )

    lecture_id = await repo.add(new_lecture)

    await process_lecture_task.kiq(lecture_id.value)  # type: ignore[call-overload]

    created = await repo.find_by_id(lecture_id)
    return created


@router.get("/", response_model=list[LectureRead])
@inject
async def list_lectures(repo: FromDishka[ILectureRepository]) -> Any:
    return await repo.find_all()


@router.get("/{lecture_id}", response_model=LectureRead)
@inject
async def get_lecture(lecture_id: str, repo: FromDishka[ILectureRepository]) -> Any:
    lecture = await repo.find_by_id(LectureId(lecture_id))
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.patch("/{lecture_id}", response_model=LectureRead)
@inject
async def update_lecture(
    lecture_id: str,
    data: LectureUpdate,
    repo: FromDishka[ILectureRepository],
) -> Any:
    lecture = await repo.find_by_id(LectureId(lecture_id))
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    lecture.update_info(
        at=datetime.now(),
        title=Title(data.title) if data.title else None,
        tags=frozenset(Tag(t) for t in data.tags) if data.tags is not None else None,
    )

    await repo.save(lecture)
    return lecture


@router.delete("/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_lecture(lecture_id: str, repo: FromDishka[ILectureRepository]) -> None:
    if not await repo.delete(LectureId(lecture_id)):
        raise HTTPException(status_code=404, detail="Lecture not found")
