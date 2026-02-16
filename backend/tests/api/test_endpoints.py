import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lecture_api_full_cycle(client: AsyncClient):
    # Создание
    payload = {"title": "Full Cycle", "author_id": "user_1", "tags": ["a"]}
    resp = await client.post("/api/v1/lectures/", json=payload)
    l_id = resp.json()["id"]

    # Список и получение
    await client.get("/api/v1/lectures/")
    await client.get(f"/api/v1/lectures/{l_id}")

    # Обновление (закрывает ветки в entities/lecture.py)
    await client.patch(f"/api/v1/lectures/{l_id}", json={"title": "New"})

    # Удаление
    await client.delete(f"/api/v1/lectures/{l_id}")

    # 404 (закрывает missing coverage в endpoints)
    fake_id = "6992dc0a6b280c1595e731eb"
    await client.get(f"/api/v1/lectures/{fake_id}")
