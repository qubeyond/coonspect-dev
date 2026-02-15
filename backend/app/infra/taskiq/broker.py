import taskiq_fastapi
from taskiq import TaskiqEvents, TaskiqState
from taskiq_redis import ListQueueBroker

from app.common.settings import settings
from app.infra.mongo.client import mongo_client

broker = ListQueueBroker(str(settings.redis_url))


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def worker_startup(state: TaskiqState) -> None:
    await mongo_client.connect()
    print("WORKER: Connected to MongoDB")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def worker_shutdown(state: TaskiqState) -> None:
    mongo_client.close()
    print("WORKER: Closed MongoDB connection")


taskiq_fastapi.init(broker, "app.main:app")
