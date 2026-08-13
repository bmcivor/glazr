import json

import redis
from django.conf import settings
from django.core.management.base import BaseCommand

from orders.exceptions import OrderError
from orders.services import create_order


def handle_message(payload: str) -> None:
    message = json.loads(payload)
    if message.get("event") != "new_donut_order":
        return
    create_order(message["data"]["donuts"])


class Command(BaseCommand):
    help = "Consume inbound order messages."

    def handle(self, *args, **options) -> None:
        client = redis.Redis.from_url(settings.REDIS_URL)
        pubsub = client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(settings.INBOUND_CHANNEL)

        for message in pubsub.listen():
            try:
                handle_message(message["data"].decode())
            except (json.JSONDecodeError, KeyError, OrderError) as exc:
                self.stderr.write(f"Skipped message: {exc}")
