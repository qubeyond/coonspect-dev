import asyncio

from bson import ObjectId

from app.api.v1.schemas.lecture import LectureStatus
from app.common.constants import MONGO_LECTURES_COLLECTION
from app.infra.mongo.client import mongo_client
from app.infra.taskiq.broker import broker


@broker.task
async def process_lecture_task(lecture_id: str) -> None:
    collection = mongo_client.db[MONGO_LECTURES_COLLECTION]
    obj_id = ObjectId(lecture_id)

    # Переводим в статус "в обработке"
    await collection.update_one(
        {"_id": obj_id}, {"$set": {"status": LectureStatus.PROCESSING}}
    )

    # Имитация выполнения STT / LLM
    await asyncio.sleep(10)

    # Завершение обработки
    await collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "status": LectureStatus.COMPLETED,
                "updated_at": asyncio.get_event_loop().time(),
            }
        },
    )
