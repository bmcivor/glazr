from collections import defaultdict
from typing import Any

from django.db import transaction

from catalogue.models import Donut
from glazr.messaging import publish_event
from orders.exceptions import (
    DonutNotFound,
    DonutUnavailable,
    InvalidOrder,
    InvalidQuantity,
    InvalidStatusChange,
)
from orders.models import Order, OrderItem


@transaction.atomic
def create_order(items: list[dict[str, Any]]) -> Order:
    """
    Create an order from a list of donut codes and quantities.

    The single entry point for both the HTTP API and the message consumer.
    Duplicate codes are merged into one line, and each line records the
    donut's price at the time of ordering, so later edits to a donut leave
    existing orders alone.

    Everything is validated before anything is written, so a rejected payload
    persists nothing.
    """
    if not items:
        raise InvalidOrder("An order must contain at least one donut.")

    quantities: dict[str, int] = defaultdict(int)

    for item in items:
        quantity = item["quantity"]
        if quantity <= 0:
            raise InvalidQuantity(
                f"Quantity for {item['donut_code']} must be greater than zero."
            )

        quantities[item["donut_code"]] += quantity

    donuts = Donut.objects.in_bulk(list(quantities), field_name="donut_code")

    for code in quantities:
        donut = donuts.get(code)
        if donut is None:
            raise DonutNotFound(f"No donut with code {code}.")
        if not donut.available:
            raise DonutUnavailable(f"{code} is not currently available.")

    order = Order.objects.create()
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                donut=donuts[code],
                quantity=quantity,
                unit_price=donuts[code].price,
            )
            for code, quantity in quantities.items()
        ]
    )

    publish_event("order.created", {"order_id": order.id, "total": order.total})

    return order


def dispatch_order(order: Order) -> Order:
    """
    Move an order from CREATED to DISPATCHED.

    The only status transition in the system. Dispatching an order that is
    already dispatched is rejected rather than ignored, so a repeat call is
    visible to the caller instead of silently succeeding.
    """
    if order.status != Order.Status.CREATED:
        raise InvalidStatusChange(
            f"Order {order.id} is {order.status} and cannot be dispatched."
        )

    order.status = Order.Status.DISPATCHED
    order.save(update_fields=["status"])

    publish_event("order.dispatched", {"order_id": order.id})

    return order
