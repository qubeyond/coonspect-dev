from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_lecture_repository
from app.api.v1.schemas.lecture import (
    LectureCreate,
    LectureRead,
    LectureStatus,
    LectureUpdate,
)
from app.domain.entities.lecture import Lecture
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.tasks.lecture import process_lecture_task

router = APIRouter()


# CREATE


@router.post("/", response_model=LectureRead, status_code=status.HTTP_201_CREATED)
async def create_lecture(
    data: LectureCreate, repo: ILectureRepository = Depends(get_lecture_repository)
) -> Any:
    new_lecture = Lecture(
        title=data.title,
        content=data.content,
        author_id=data.author_id,
        tags=data.tags,
        status=LectureStatus.PENDING.value,
    )

    lecture_id = await repo.create(new_lecture)

    await process_lecture_task.kiq(str(lecture_id))

    return await repo.get_by_id(lecture_id)


# READ


@router.get("/", response_model=list[LectureRead])
async def list_lectures(
    repo: ILectureRepository = Depends(get_lecture_repository),
) -> Any:
    return await repo.find_many()


@router.get("/{lecture_id}", response_model=LectureRead)
async def get_lecture(
    lecture_id: str, repo: ILectureRepository = Depends(get_lecture_repository)
) -> Any:
    lecture = await repo.get_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


# UPDATE


@router.patch("/{lecture_id}", response_model=LectureRead)
async def update_lecture(
    lecture_id: str,
    data: LectureUpdate,
    repo: ILectureRepository = Depends(get_lecture_repository),
) -> Any:
    lecture = await repo.get_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(lecture, key, value)

    await repo.update(lecture)
    return lecture


# DELETE


@router.delete("/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lecture(
    lecture_id: str, repo: ILectureRepository = Depends(get_lecture_repository)
) -> None:
    if not await repo.delete(lecture_id):
        raise HTTPException(status_code=404, detail="Lecture not found")
