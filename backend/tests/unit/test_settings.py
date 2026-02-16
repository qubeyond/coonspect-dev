from app.common.settings import settings


def test_settings_redis_url():
    """Кейс: Покрытие вычисляемого поля redis_url"""
    url = settings.redis_url
    assert "redis://" in url
    assert str(settings.REDIS_PORT) in url
