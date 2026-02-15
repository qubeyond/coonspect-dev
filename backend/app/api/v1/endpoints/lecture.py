from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.entities.lecture import Lecture
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.api.deps import get_lecture_repository
from app.api.v1.schemas.lecture import LectureCreate, LectureRead, LectureUpdate


router = APIRouter()


@router.post("/", response_model=LectureRead, status_code=status.HTTP_201_CREATED)
async def create_lecture(
    data: LectureCreate, 
    repo: ILectureRepository = Depends(get_lecture_repository)
):
    new_lecture = Lecture(
        title=data.title,
        content=data.content,
        author_id=data.author_id,
        tags=data.tags
    )
    lecture_id = await repo.create(new_lecture)
    return await repo.get_by_id(lecture_id)

@router.get("/", response_model=list[LectureRead])
async def list_lectures(repo: ILectureRepository = Depends(get_lecture_repository)):
    return await repo.find_many()

@router.get("/{lecture_id}", response_model=LectureRead)
async def get_lecture(lecture_id: str, repo: ILectureRepository = Depends(get_lecture_repository)):
    lecture = await repo.get_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@router.patch("/{lecture_id}", response_model=LectureRead)
async def update_lecture(
    lecture_id: str, 
    data: LectureUpdate, 
    repo: ILectureRepository = Depends(get_lecture_repository)
):
    lecture = await repo.get_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(lecture, key, value)
        
    await repo.update(lecture)
    return lecture

@router.delete("/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lecture(lecture_id: str, repo: ILectureRepository = Depends(get_lecture_repository)):
    if not await repo.delete(lecture_id):
        raise HTTPException(status_code=404, detail="Lecture not found")