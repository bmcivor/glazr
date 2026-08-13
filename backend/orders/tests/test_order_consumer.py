import json
from decimal import Decimal

from django.test import TestCase

from catalogue.models import Donut
from orders.management.commands.run_consumer import handle_message
from orders.models import Order


class TestHandleMessage(TestCase):
    def setUp(self) -> None:
        Donut.objects.create(
            donut_code="THE_HOMER",
            description="Pink with sprinkles",
            price=Decimal("4.50"),
        )

    def test_new_donut_order_creates_an_order(self) -> None:
        """
        Setup: An available donut and a valid new_donut_order message.

        Expectations: An order is created with a line for that donut.
        """
        handle_message(
            json.dumps(
                {
                    "event": "new_donut_order",
                    "data": {"donuts": [{"donut_code": "THE_HOMER", "quantity": 2}]},
                }
            )
        )

        order = Order.objects.get()
        assert order.items.count() == 1
        assert order.total == Decimal("9.00")
