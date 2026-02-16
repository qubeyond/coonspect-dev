from typing import Any

from dishka import make_async_container
from dishka.integrations.fastapi import FromDishka, inject, setup_dishka
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.api.v1.router import v1_router
from app.common.settings import settings
from app.infra.ioc import AppProvider


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

    # 1. Создаем контейнер зависимостей
    container = make_async_container(AppProvider())

    # 2. Интегрируем Dishka в FastAPI.
    # Это само управляет жизненным циклом (заменяет старый lifespan)
    setup_dishka(container, app)

    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()


@app.get("/", response_class=HTMLResponse)
@inject
async def root_page(
    db: FromDishka[AsyncIOMotorDatabase[Any]], redis: FromDishka[Redis]
) -> Any:
    try:
        await db.command("ping")
        mongo_status = "Connected"
    except Exception:
        mongo_status = "Disconnected"

    try:
        await redis.ping()  # type: ignore
        redis_status = "Connected"
    except Exception:
        redis_status = "Disconnected"

    mongo_color = "bg-green-500" if mongo_status == "Connected" else "bg-red-500"
    redis_color = "bg-green-500" if redis_status == "Connected" else "bg-red-500"

    # ruff: noqa: E501
    return HTMLResponse(
        content=f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Coonspect Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @keyframes pulse-slow {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .animate-pulse-slow {{ animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}
        </style>
    </head>
    <body class="bg-slate-50 min-h-screen p-8 font-sans">
        <div class="max-w-5xl mx-auto">
            <header class="flex justify-between items-center mb-10 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div>
                    <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Coonspect <span class="text-indigo-600">API</span></h1>
                    <div class="flex gap-4 mt-3 text-xs font-bold uppercase tracking-wider">
                        <span class="flex items-center px-2 py-1 bg-slate-100 rounded-md">
                            <span class="w-2 h-2 rounded-full mr-2 {mongo_color}"></span>
                            Mongo: <span class="ml-1 text-slate-500">{mongo_status}</span>
                        </span>
                        <span class="flex items-center px-2 py-1 bg-slate-100 rounded-md">
                            <span class="w-2 h-2 rounded-full mr-2 {redis_color}"></span>
                            Redis: <span class="ml-1 text-slate-500">{redis_status}</span>
                        </span>
                    </div>
                </div>
                <a href="/docs" class="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-xl font-semibold hover:bg-indigo-100 transition-colors">Swagger UI</a>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="md:col-span-1">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 sticky top-8">
                        <h2 class="text-xl font-bold mb-6 text-slate-800">Новая лекция</h2>
                        <div class="space-y-4">
                            <input id="title" type="text" placeholder="Название лекции" class="w-full border-slate-200 border p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none">
                            <button onclick="createLecture()" class="bg-indigo-600 text-white px-4 py-3 rounded-xl w-full font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all active:scale-95">Создать</button>
                        </div>
                    </div>
                </div>

                <div class="md:col-span-2">
                    <div id="lecture-list" class="space-y-4"></div>
                </div>
            </div>
        </div>

        <script>
            const API_URL = '/api/v1/lectures/';
            
            function getStatusStyle(status) {{
                switch(status) {{
                    case 'pending': return 'bg-amber-50 text-amber-700 border-amber-100';
                    case 'processing': return 'bg-indigo-50 text-indigo-700 border-indigo-100 animate-pulse-slow';
                    case 'completed': return 'bg-emerald-50 text-emerald-700 border-emerald-100';
                    case 'failed': return 'bg-red-50 text-red-700 border-red-100';
                    default: return 'bg-slate-50 text-slate-700';
                }}
            }}

            async function fetchLectures() {{
                try {{
                    const res = await fetch(API_URL);
                    if (!res.ok) throw new Error('Ошибка сервера');
                    const data = await res.json();
                    
                    document.getElementById('lecture-list').innerHTML = data.map(l => {{
                        const titleStr = typeof l.title === 'object' ? l.title.value : l.title;
                        const dateStr = l.registered_at || l.created_at;

                        return `
                        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="text-lg font-bold text-slate-800">${{titleStr}}</h3>
                                    <p class="text-xs text-slate-400 font-mono mt-1">ID: ${{l.id}}</p>
                                </div>
                                <span class="px-3 py-1 rounded-full text-xs font-bold border ${{getStatusStyle(l.status)}} uppercase tracking-widest">
                                    ${{l.status}}
                                </span>
                            </div>
                            
                            <div class="bg-slate-50 p-3 rounded-lg">
                                 <pre class="text-[10px] text-slate-500 overflow-x-auto">${{JSON.stringify(l.content || 'Нет контента', null, 2)}}</pre>
                            </div>

                            <div class="flex justify-between items-center pt-2 border-t border-slate-50">
                                <span class="text-[10px] text-slate-400 uppercase font-bold italic">
                                    Создано: ${{dateStr ? new Date(dateStr).toLocaleString() : '---'}}
                                </span>
                                <button onclick="deleteLecture('${{l.id}}')" class="text-red-400 hover:text-red-600 text-xs font-bold uppercase transition-colors">Удалить</button>
                            </div>
                        </div>
                    `}}).join('');
                }} catch (e) {{
                    console.error("Fetch error:", e);
                }}
            }}

            async function createLecture() {{
                const title = document.getElementById('title').value;
                if (!title) return alert('Введите название');

                await fetch(API_URL, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        title: title,
                        author_id: "admin_user",
                        tags: ["auto-web"]
                    }})
                }});
                document.getElementById('title').value = '';
                fetchLectures();
            }}

            async function deleteLecture(id) {{
                if(!confirm('Удалить лекцию?')) return;
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
@inject
async def health_check(
    db: FromDishka[AsyncIOMotorDatabase[Any]], redis: FromDishka[Redis]
) -> Any:
    try:
        await redis.ping()  # type: ignore[misc]
        redis_ok = True
    except Exception:
        redis_ok = False

    try:
        await db.command("ping")
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
