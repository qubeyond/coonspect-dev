from collections.abc import AsyncIterable
from typing import Any

import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.infra.ioc import AppProvider
from app.main import app  # Убедись, что путь к FastAPI app верный


class TestProvider(Provider):
    @provide(scope=Scope.APP, override=True)
    def get_db(self, client: AsyncIOMotorClient[Any]) -> AsyncIOMotorDatabase[Any]:
        return client["test_database_for_unit_tests"]


@pytest_asyncio.fixture(scope="session")
async def container() -> AsyncIterable[AsyncContainer]:
    # Создаем контейнер вручную
    container = make_async_container(AppProvider(), TestProvider())
    yield container
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def client(container: AsyncContainer) -> AsyncIterable[AsyncClient]:
    """Тестовый клиент для API, который знает про наш контейнер"""
    from dishka.integrations.fastapi import setup_dishka

    # Привязываем наш тестовый контейнер к приложению
    setup_dishka(container, app)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def db_client(
    container: AsyncContainer,
) -> AsyncIterable[AsyncIOMotorDatabase[Any]]:
    """Фикстура для очистки БД после каждого теста"""
    db = await container.get(AsyncIOMotorDatabase[Any])
    yield db
    await db.client.drop_database(db.name)
