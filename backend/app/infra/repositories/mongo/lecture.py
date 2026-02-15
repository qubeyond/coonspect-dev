from bson import ObjectId
from pymongo.errors import PyMongoError

from app.domain.entities.lecture import Lecture
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.infra.mongo.client import mongo_client
from app.common.constants import MONGO_LECTURES_COLLECTION


class MongoLectureRepository(ILectureRepository):
    def __init__(self) -> None:
        self._collection_name = MONGO_LECTURES_COLLECTION

    @property
    def collection(self):
        return mongo_client.db[self._collection_name]

    async def create(self, lecture: Lecture) -> str:
        doc = {
            "title": lecture.title,
            "content": lecture.content,
            "author_id": lecture.author_id,
            "tags": lecture.tags,
            "created_at": lecture.created_at,
            "updated_at": lecture.updated_at
        }
        try:
            result = await self.collection.insert_one(doc)
            return str(result.inserted_id)

        except PyMongoError as e:
            print(f"Error creating lecture: {e}")
            raise

    async def get_by_id(self, lecture_id: str) -> Lecture | None:
        if not ObjectId.is_valid(lecture_id):
            return None

        try:
            doc = await self.collection.find_one({"_id": ObjectId(lecture_id)})
            if not doc:
                return None
            return self._map_to_entity(doc)

        except PyMongoError as e:
            print(f"Error fetching lecture {lecture_id}: {e}")
            return None

    async def update(self, lecture: Lecture) -> None:
        if not lecture.id or not ObjectId.is_valid(lecture.id):
            return

        update_data = {
            "title": lecture.title,
            "content": lecture.content,
            "author_id": lecture.author_id,
            "tags": lecture.tags,
            "updated_at": lecture.updated_at
        }
        try:
            await self.collection.update_one(
                {"_id": ObjectId(lecture.id)},
                {"$set": update_data}
            )

        except PyMongoError as e:
            print(f"Error updating lecture {lecture.id}: {e}")
            raise

    async def delete(self, lecture_id: str) -> bool:
        if not ObjectId.is_valid(lecture_id):
            return False

        try:
            result = await self.collection.delete_one({"_id": ObjectId(lecture_id)})
            return result.deleted_count > 0

        except PyMongoError as e:
            print(f"Error deleting lecture {lecture_id}: {e}")
            return False

    async def find_many(
        self, 
        *, 
        limit: int = 10, 
        offset: int = 0, 
        author_id: str | None = None
    ) -> list[Lecture]:
        query = {}
        if author_id:
            query["author_id"] = author_id

        try:
            cursor = self.collection.find(query).skip(offset).limit(limit)
            return [self._map_to_entity(doc) async for doc in cursor]

        except PyMongoError as e:
            print(f"Error finding lectures: {e}")
            return []

    async def count(self, author_id: str | None = None) -> int:
        query = {"author_id": author_id} if author_id else {}
        try:
            return await self.collection.count_documents(query)
            
        except PyMongoError as e:
            print(f"Error counting lectures: {e}")
            return 0

    def _map_to_entity(self, doc: dict) -> Lecture:
        """Вспомогательный метод для маппинга документа Mongo в Entity."""
        return Lecture(
            id=str(doc["_id"]),
            title=doc["title"],
            content=doc["content"],
            author_id=doc.get("author_id"),
            tags=doc.get("tags", []),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )