from app.domain.interfaces.lecture_repo import ILectureRepository
from app.infra.mongo.client import mongo_client
from app.infra.repositories.mongo.lecture import MongoLectureRepository


def get_lecture_repository() -> ILectureRepository:
    return MongoLectureRepository(mongo_client.db)
