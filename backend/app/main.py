from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.common.settings import settings
from app.infra.mongo.client import mongo_client
from app.api.v1.router import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт приложения
    await mongo_client.connect()
    yield
    # Остановка приложения
    mongo_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan
)

# Подключаем роутер со всеми CRUD методами
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Coonspect Admin</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <header class="flex justify-between items-center mb-8 bg-white p-6 rounded-lg shadow-sm">
                <h1 class="text-2xl font-bold text-indigo-600">Coonspect API Explorer</h1>
                <a href="/docs" class="text-sm text-gray-500 hover:text-indigo-500 underline">Swagger UI</a>
            </header>

            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-lg font-semibold mb-4">Создать новую лекцию</h2>
                <div class="grid grid-cols-1 gap-4">
                    <input id="title" type="text" placeholder="Заголовок лекции" class="border p-2 rounded w-full">
                    <textarea id="content" placeholder='Контент (JSON, например {"text": "hello"})' class="border p-2 rounded w-full h-20"></textarea>
                    <button onclick="createLecture()" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition">
                        Создать лекцию
                    </button>
                </div>
            </div>

            <div class="space-y-4" id="lecture-list">
                <p class="text-gray-500 text-center">Загрузка лекций...</p>
            </div>
        </div>

        <script>
            const API_URL = '/api/v1/lectures/';

            // GET - Получить все
            async function fetchLectures() {
                try {
                    const res = await fetch(API_URL);
                    const lectures = await res.json();
                    const container = document.getElementById('lecture-list');
                    
                    if (lectures.length === 0) {
                        container.innerHTML = '<div class="text-center p-8 bg-white rounded shadow text-gray-400">Лекций пока нет</div>';
                        return;
                    }

                    container.innerHTML = lectures.map(l => `
                        <div class="bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500 flex justify-between items-start">
                            <div>
                                <h3 class="font-bold text-xl">${l.title}</h3>
                                <p class="text-sm text-gray-400 mb-2 italic">ID: ${l.id}</p>
                                <pre class="text-xs bg-gray-50 p-2 rounded text-gray-600">${JSON.stringify(l.content)}</pre>
                            </div>
                            <div class="flex flex-col gap-2">
                                <button onclick="deleteLecture('${l.id}')" class="text-red-500 hover:bg-red-50 p-2 rounded border border-red-100 text-sm">
                                    Удалить
                                </button>
                                <button onclick="alert('ID скопирован: ' + '${l.id}')" class="text-gray-500 hover:bg-gray-50 p-2 rounded border border-gray-100 text-sm">
                                    Инфо
                                </button>
                            </div>
                        </div>
                    `).join('');
                } catch (e) {
                    console.error('Error:', e);
                }
            }

            // POST - Создать
            async function createLecture() {
                const title = document.getElementById('title').value;
                let content = {};
                try {
                    const rawContent = document.getElementById('content').value;
                    content = rawContent ? JSON.parse(rawContent) : {"text": "empty"};
                } catch (e) {
                    alert("Ошибка в формате JSON контента!");
                    return;
                }

                await fetch(API_URL, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ title, content, tags: ["web-ui"] })
                });
                
                document.getElementById('title').value = '';
                document.getElementById('content').value = '';
                fetchLectures();
            }

            // DELETE - Удалить
            async function deleteLecture(id) {
                if (!confirm('Точно удалить?')) return;
                await fetch(API_URL + id, { method: 'DELETE' });
                fetchLectures();
            }

            // Инициализация
            fetchLectures();
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "database": "connected" if mongo_client.db is not None else "error"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)