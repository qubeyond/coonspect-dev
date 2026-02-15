from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.v1.router import v1_router
from app.common.settings import settings
from app.infra.mongo.client import mongo_client
from app.infra.redis.client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await mongo_client.connect()
    try:
        await redis_client.ping()
        print("BASE: Redis connected")
    except Exception as e:
        print(f"BASE: Redis error: {e}")
    yield
    mongo_client.close()
    await redis_client.aclose()


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root_page() -> Any:
    mongo_ok = False
    try:
        if mongo_client.db is not None:
            mongo_ok = True
    except Exception:
        mongo_ok = False

    mongo_status = "Connected" if mongo_ok else "Disconnected"

    try:
        await redis_client.ping()
        redis_status = "Connected"
    except Exception:
        redis_status = "Disconnected"

    # ruff: noqa: E501
    return HTMLResponse(
        content=f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Coonspect Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <header class="flex justify-between items-center mb-8 bg-white p-6 rounded-lg shadow-sm">
                <div>
                    <h1 class="text-2xl font-bold text-indigo-600">Coonspect API Explorer</h1>
                    <div class="flex gap-4 mt-2 text-xs font-mono">
                        <span class="flex items-center">
                            <span class="w-2 h-2 rounded-full mr-2 {"bg-green-500" if mongo_status == "Connected" else "bg-red-500"}"></span>
                            Mongo: {mongo_status}
                        </span>
                        <span class="flex items-center">
                            <span class="w-2 h-2 rounded-full mr-2 {"bg-green-500" if redis_status == "Connected" else "bg-red-500"}"></span>
                            Redis: {redis_status}
                        </span>
                    </div>
                </div>
                <div class="flex items-center gap-4">
                    <a href="/docs" class="text-sm text-gray-500 hover:text-indigo-500 underline">Swagger UI</a>
                </div>
            </header>
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-lg font-semibold mb-4">Создать лекцию</h2>
                <input id="title" type="text" placeholder="Заголовок" class="border p-2 mb-4 rounded w-full">
                <textarea id="content" placeholder='JSON' class="border p-2 mb-4 rounded w-full h-20"></textarea>
                <button onclick="createLecture()" class="bg-indigo-600 text-white px-4 py-2 rounded w-full">Создать</button>
            </div>
            <div id="lecture-list" class="space-y-4"></div>
        </div>
        <script>
            const API_URL = '/api/v1/lectures/';
            async function fetchLectures() {{
                const res = await fetch(API_URL);
                const data = await res.json();
                document.getElementById('lecture-list').innerHTML = data.map(l => `
                    <div class="bg-white p-4 rounded shadow flex justify-between">
                        <div>
                            <p class="font-bold">${{l.title}}</p>
                            <p class="text-xs text-gray-400">${{l.status}}</p>
                        </div>
                        <button onclick="deleteLecture('${{l.id}}')" class="text-red-500 text-sm">Удалить</button>
                    </div>
                `).join('');
            }}
            async function createLecture() {{
                const title = document.getElementById('title').value;
                const content = JSON.parse(document.getElementById('content').value || '{{}}');
                await fetch(API_URL, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{title, content, author_id: "admin"}})
                }});
                fetchLectures();
            }}
            async function deleteLecture(id) {{
                await fetch(API_URL + id, {{method: 'DELETE'}});
                fetchLectures();
            }}
            fetchLectures();
            setInterval(fetchLectures, 5000);
        </script>
    </body>
    </html>
    """
    )


@app.get("/health")
async def health_check() -> dict[str, Any]:
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    mongo_ok = False
    try:
        if mongo_client.db is not None:
            mongo_ok = True
    except Exception:
        mongo_ok = False

    return {
        "status": "ok" if mongo_ok and redis_ok else "error",
        "services": {
            "mongodb": "connected" if mongo_ok else "error",
            "redis": "connected" if redis_ok else "error",
        },
    }
