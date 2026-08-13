import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Q

from catalogue.models import Donut


class Order(models.Model):
    """
    A customer's order, placed over HTTP or received as a message.

    Carries no total. It is derived from the lines, so storing it would let
    the two disagree.
    """

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        DISPATCHED = "DISPATCHED", "Dispatched"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.id} ({self.status})"

    @property
    def total(self) -> Decimal:
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class OrderItem(models.Model):
    """
    One donut selection on an order.

    unit_price is the donut's price at the time the order was placed. Reading
    it live would mean editing a donut rewrote the totals of every past order.

    Quantity is enforced to a Positive Integer here, but use a CheckConstraint
    to ensure it is greater than zero.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    donut = models.ForeignKey(
        Donut, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="order_item_quantity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.donut.donut_code}"

    @property
    def line_total(self) -> Decimal:
        return self.quantity * self.unit_price
