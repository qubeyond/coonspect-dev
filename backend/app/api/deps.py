from app.infra.repositories.mongo.lecture import MongoLectureRepository
from app.domain.interfaces.lecture_repo import ILectureRepository

def get_lecture_repository() -> ILectureRepository:
    return MongoLectureRepository()