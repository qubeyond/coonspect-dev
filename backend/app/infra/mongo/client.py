from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.common.settings import settings
from app.common.constants import MONGO_TIMEOUT_MS


class MongoClient:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db = None

    async def connect(self) -> None:
        try:
            self._client = AsyncIOMotorClient(
                settings.mongo_url,
                serverSelectionTimeoutMS=MONGO_TIMEOUT_MS
            )
            await self._client.admin.command('ping')
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
    def db(self):
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db


mongo_client = MongoClient()