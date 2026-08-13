import json
from typing import Any, Protocol

import redis
from django.conf import settings
from django.db import transaction


class EventPublisher(Protocol):
    def publish(self, event: str, data: dict[str, Any]) -> None: ...


class RedisEventPublisher:
    def __init__(self, url: str, channel: str) -> None:
        self._client = redis.Redis.from_url(url)
        self._channel = channel

    def publish(self, event: str, data: dict[str, Any]) -> None:
        self._client.publish(
            self._channel,
            json.dumps({"event": event, "data": data}, default=str),
        )


class RecordingEventPublisher:
    def __init__(self) -> None:
        self.published: list[dict[str, Any]] = []

    def publish(self, event: str, data: dict[str, Any]) -> None:
        self.published.append({"event": event, "data": data})


_publisher: EventPublisher | None = None


def get_publisher() -> EventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = RedisEventPublisher(settings.REDIS_URL, settings.EVENT_CHANNEL)
    return _publisher


def set_publisher(publisher: EventPublisher) -> None:
    global _publisher
    _publisher = publisher


def publish_event(event: str, data: dict[str, Any]) -> None:
    transaction.on_commit(lambda: get_publisher().publish(event, data))
