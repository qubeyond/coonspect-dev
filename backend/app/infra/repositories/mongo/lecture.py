from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.common.constants import MONGO_LECTURES_COLLECTION
from app.domain.entities.lecture import Lecture
from app.domain.interfaces.lecture_repo import ILectureRepository


class MongoLectureRepository(ILectureRepository):
    def __init__(self, db: AsyncIOMotorDatabase[Any]) -> None:
        self._db = db
        self._collection_name = MONGO_LECTURES_COLLECTION

    @property
    def collection(self) -> Any:
        return self._db[self._collection_name]

    # WRITE

    async def create(self, lecture: Lecture) -> str:
        doc: dict[str, Any] = {
            "title": lecture.title,
            "content": lecture.content,
            "author_id": lecture.author_id,
            "tags": lecture.tags,
            "status": getattr(lecture, "status", "pending"),
            "created_at": lecture.created_at,
            "updated_at": lecture.updated_at,
        }

        try:
            result = await self.collection.insert_one(doc)
            return str(result.inserted_id)

        except PyMongoError as e:  # pragma: no cover
            print(f"Error creating lecture: {e}")
            raise

    # READ

    async def get_by_id(self, lecture_id: str) -> Lecture | None:
        if not ObjectId.is_valid(lecture_id):
            return None

        try:
            doc = await self.collection.find_one({"_id": ObjectId(lecture_id)})
            return self._map_to_entity(doc) if doc else None

        except PyMongoError as e:  # pragma: no cover
            print(f"Error fetching lecture {lecture_id}: {e}")
            return None

    async def find_many(
        self, *, limit: int = 10, offset: int = 0, author_id: str | None = None
    ) -> list[Lecture]:
        query = {"author_id": author_id} if author_id else {}
        try:
            cursor = self.collection.find(query).skip(offset).limit(limit)
            return [self._map_to_entity(doc) async for doc in cursor]

        except PyMongoError as e:  # pragma: no cover
            print(f"Error finding lectures: {e}")
            return []

    async def count(self, author_id: str | None = None) -> int:
        query = {"author_id": author_id} if author_id else {}
        try:
            result = await self.collection.count_documents(query)
            return int(result)

        except PyMongoError as e:  # pragma: no cover
            print(f"Error counting lectures: {e}")
            return 0

    # UPDATE/DELETE

    async def update(self, lecture: Lecture) -> None:
        if not lecture.id or not ObjectId.is_valid(lecture.id):
            return

        update_data: dict[str, Any] = {
            "title": lecture.title,
            "content": lecture.content,
            "author_id": lecture.author_id,
            "tags": lecture.tags,
            "status": getattr(lecture, "status", "pending"),
            "updated_at": lecture.updated_at,
        }

        try:
            await self.collection.update_one(
                {"_id": ObjectId(lecture.id)}, {"$set": update_data}
            )

        except PyMongoError as e:  # pragma: no cover
            print(f"Error updating lecture {lecture.id}: {e}")
            raise

    async def delete(self, lecture_id: str) -> bool:
        if not ObjectId.is_valid(lecture_id):
            return False

        try:
            result = await self.collection.delete_one({"_id": ObjectId(lecture_id)})
            return bool(result.deleted_count > 0)

        except PyMongoError as e:  # pragma: no cover
            print(f"Error deleting lecture {lecture_id}: {e}")
            return False

    # HELPERS

    def _map_to_entity(self, doc: dict[str, Any]) -> Lecture:
        return Lecture(
            id=str(doc["_id"]),
            title=doc["title"],
            content=doc["content"],
            author_id=doc.get("author_id"),
            tags=doc.get("tags", []),
            status=doc.get("status", "pending"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
