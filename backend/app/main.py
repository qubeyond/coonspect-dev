from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.common.settings import settings
from app.infra.mongo.client import mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Действие при СТАРТЕ ---
    # Пытаемся подключиться к базе
    await mongo_client.connect()
    yield
    # --- Действие при ВЫКЛЮЧЕНИИ ---
    mongo_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    # Можно добавить проверку, что база реально жива
    return {
        "status": "ok",
        "version": "0.1.0",
        "database": "connected"  # Если мы дошли сюда, значит lifespan отработал
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)