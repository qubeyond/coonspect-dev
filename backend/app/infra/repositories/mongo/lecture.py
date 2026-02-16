from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.constants import MONGO_LECTURES_COLLECTION
from app.domain.entities.lecture import Lecture, LectureStatus
from app.domain.entities.value_objects import (
    AuthorId,
    LectureId,
    Tag,
    Title,
    Transcript,
)
from app.domain.interfaces.lecture_repo import ILectureRepository


class MongoLectureRepository(ILectureRepository):
    def __init__(self, db: AsyncIOMotorDatabase[Any]) -> None:
        self._db = db
        self._collection = db[MONGO_LECTURES_COLLECTION]

    async def add(self, lecture: Lecture) -> LectureId:
        doc = self._entity_to_doc(lecture)
        result = await self._collection.insert_one(doc)
        return LectureId(str(result.inserted_id))

    async def save(self, lecture: Lecture) -> None:
        if not lecture.id or not ObjectId.is_valid(lecture.id.value):
            raise ValueError("Entity must have a valid ID to be saved")

        doc = self._entity_to_doc(lecture)
        await self._collection.replace_one({"_id": ObjectId(lecture.id.value)}, doc)

    async def delete(self, lecture_id: LectureId) -> bool:
        if not ObjectId.is_valid(lecture_id.value):
            return False

        result = await self._collection.delete_one({"_id": ObjectId(lecture_id.value)})
        return result.deleted_count > 0

    async def find_by_id(self, lecture_id: LectureId) -> Lecture | None:
        if not ObjectId.is_valid(lecture_id.value):
            return None

        doc = await self._collection.find_one({"_id": ObjectId(lecture_id.value)})
        return self._map_to_entity(doc) if doc else None

    async def find_all(
        self, *, limit: int = 10, offset: int = 0, author_id: AuthorId | None = None
    ) -> list[Lecture]:
        query = {"author_id": author_id.value} if author_id else {}
        cursor = self._collection.find(query).skip(offset).limit(limit)
        return [self._map_to_entity(doc) async for doc in cursor]

    async def count(self, author_id: AuthorId | None = None) -> int:
        query = {"author_id": author_id.value} if author_id else {}
        return await self._collection.count_documents(query)

    # Helpers

    def _entity_to_doc(self, lecture: Lecture) -> dict[str, Any]:
        return {
            "title": lecture.title.value,
            "author_id": lecture.author_id.value,
            "status": str(lecture.status),
            "tags": [tag.value for tag in lecture.tags],
            "transcript": {
                "text": lecture.content.text,
                "language": lecture.content.language,
                "confidence": lecture.content.confidence,
            }
            if lecture.content
            else None,
            "registered_at": lecture.registered_at,
            "updated_at": lecture.updated_at,
            "published_at": lecture.published_at,
        }

    def _map_to_entity(self, doc: dict[str, Any]) -> Lecture:
        transcript_data = doc.get("transcript")

        transcript = (
            Transcript(
                text=transcript_data["text"],
                language=transcript_data.get("language"),
                confidence=transcript_data.get("confidence"),
            )
            if transcript_data
            else None
        )

        return Lecture(
            id=LectureId(str(doc["_id"])),
            author_id=AuthorId(doc["author_id"]),
            title=Title(doc["title"]),
            content=transcript,
            tags=frozenset(Tag(t) for t in doc.get("tags", [])),
            status=LectureStatus(doc["status"]),
            registered_at=doc["registered_at"],
            updated_at=doc["updated_at"],
            published_at=doc.get("published_at"),
        )
