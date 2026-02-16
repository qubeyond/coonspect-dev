from collections.abc import AsyncIterable
from typing import Any

from dishka import Provider, Scope, provide
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import Redis, from_url

from app.common.settings import settings
from app.domain.interfaces.lecture_repo import ILectureRepository
from app.infra.repositories.mongo.lecture import MongoLectureRepository

# TODO:
# 1. Разбить на провайдеры


class AppProvider(Provider):
    # Infra

    @provide(scope=Scope.APP)
    async def get_mongo_client(self) -> AsyncIterable[AsyncIOMotorClient[Any]]:
        client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(
            str(settings.mongo_url), serverSelectionTimeoutMS=5000
        )
        yield client
        client.close()

    @provide(scope=Scope.APP)
    def get_db(self, client: AsyncIOMotorClient[Any]) -> AsyncIOMotorDatabase[Any]:
        return client[settings.MONGO_DB_NAME]

    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[Redis]:
        client = from_url(str(settings.redis_url), decode_responses=True)  # type: ignore
        yield client
        await client.aclose()

    # Repos

    @provide(scope=Scope.REQUEST)
    def get_lecture_repo(self, db: AsyncIOMotorDatabase[Any]) -> ILectureRepository:
        return MongoLectureRepository(db)
