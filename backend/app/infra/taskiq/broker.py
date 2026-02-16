from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import ListQueueBroker

from app.common.settings import settings
from app.infra.ioc import AppProvider

container = make_async_container(AppProvider())
broker = ListQueueBroker(str(settings.redis_url))

setup_dishka(container, broker)
