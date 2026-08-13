import uuid

from django.db import models


class Donut(models.Model):
    """
    An item in the catalogue that customers can order.

    Orders reference donuts by donut_code rather than by id. It is the
    identifier both the HTTP payload and the inbound order message use,
    which is why it is unique.

    available gates whether a donut can be ordered.

    price is per unit, and is copied onto the order when placed so editing
    the field does not edit previous orders.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donut_code = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ["donut_code"]

    def __str__(self) -> str:
        return f"{self.donut_code} — {self.description}"
