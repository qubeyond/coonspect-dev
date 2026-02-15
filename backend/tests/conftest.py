import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.settings import settings


@pytest.fixture(scope="session")
async def db_client():
    client = AsyncIOMotorClient(str(settings.mongo_url), serverSelectionTimeoutMS=5000)

    await client.admin.command("ping")

    db = client[settings.MONGO_DB_NAME]
    yield db

    client.close()
