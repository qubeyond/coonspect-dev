from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.common.constants import MONGO_TIMEOUT_MS
from app.common.settings import settings


class MongoClient:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient[Any] | None = None
        self._db: AsyncIOMotorDatabase[Any] | None = None

    async def connect(self) -> None:
        try:
            self._client = AsyncIOMotorClient(
                str(settings.mongo_url), serverSelectionTimeoutMS=MONGO_TIMEOUT_MS
            )
            await self._client.admin.command("ping")
            self._db = self._client[settings.MONGO_DB_NAME]
            print("Successfully connected to MongoDB")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Could not connect to MongoDB: {e}")
            raise e

    def close(self) -> None:
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

    @property
    def db(self) -> AsyncIOMotorDatabase[Any]:
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db


mongo_client = MongoClient()
