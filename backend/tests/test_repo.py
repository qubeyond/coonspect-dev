import pytest
from bson import ObjectId

from app.domain.entities.lecture import Lecture
from app.infra.repositories.mongo.lecture import MongoLectureRepository


@pytest.mark.asyncio(loop_scope="session")
async def test_mongo_repo_full_cycle(db_client):
    """Кейс: Полный цикл CRUD для репозитория лекций"""
    repo = MongoLectureRepository(db_client)

    new_lecture = Lecture(
        title="Тест покрытия", content={"text": "Hello world"}, status="pending"
    )
    lecture_id = await repo.create(new_lecture)
    assert lecture_id is not None

    fetched = await repo.get_by_id(lecture_id)
    assert fetched.title == "Тест покрытия"

    fetched.title = "Обновленное название"
    fetched.status = "processed"
    await repo.update(fetched)

    after_update = await repo.get_by_id(lecture_id)
    assert after_update.status == "processed"
    assert after_update.title == "Обновленное название"

    all_lectures = await repo.find_many(limit=10)
    assert len(all_lectures) >= 1
    assert any(lecture.id == lecture_id for lecture in all_lectures)

    total = await repo.count()
    assert total >= 1

    deleted = await repo.delete(lecture_id)
    assert deleted is True

    not_found = await repo.get_by_id(lecture_id)
    assert not_found is None


@pytest.mark.asyncio(loop_scope="session")
async def test_mongo_repo_get_non_existent(db_client):
    """Кейс: Получение лекции по несуществующему ObjectId"""
    repo = MongoLectureRepository(db_client)
    random_id = str(ObjectId())
    result = await repo.get_by_id(random_id)
    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_mongo_repo_delete_non_existent(db_client):
    """Кейс: Удаление несуществующей лекции"""
    repo = MongoLectureRepository(db_client)
    success = await repo.delete(str(ObjectId()))
    assert success is False


@pytest.mark.asyncio(loop_scope="session")
async def test_mongo_repo_complex_queries(db_client):
    """Кейс: Сложные запросы (фильтрация по автору, лимиты, смещения)"""
    repo = MongoLectureRepository(db_client)
    author_id = "test_author_123"

    for i in range(3):
        lecture_obj = Lecture(
            title=f"Lecture {i}",
            content={"data": i},
            author_id=author_id,
            status="pending",
        )
        await repo.create(lecture_obj)

    # Поиск с фильтром и лимитом
    results = await repo.find_many(author_id=author_id, limit=2)
    assert len(results) == 2

    # Поиск со смещением
    offset_results = await repo.find_many(author_id=author_id, offset=2, limit=10)
    assert len(offset_results) >= 1

    # Подсчет по автору
    total_author = await repo.count(author_id=author_id)
    assert total_author >= 3

    # Валидация некорректного формата ID
    assert await repo.get_by_id("not-a-valid-object-id") is None


@pytest.mark.asyncio(loop_scope="session")
async def test_mongo_repo_invalid_inputs(db_client):
    """Кейс: Проверка раннего выхода (return) при невалидных ID"""
    repo = MongoLectureRepository(db_client)

    # update с лекцией без ID
    invalid_lecture = Lecture(title="No ID", content={})
    assert await repo.update(invalid_lecture) is None

    # delete с невалидным ObjectId
    assert await repo.delete("not-a-valid-id") is False


def test_lecture_entity_logic():
    """Кейс: Тестирование метода обновления полей сущности"""
    lecture = Lecture(title="Original", content={"x": 1})

    lecture.update(title="New Title", content={"new": "content"}, tags=["new", "tags"])

    assert lecture.title == "New Title"
    assert lecture.content == {"new": "content"}
    assert "new" in lecture.tags
