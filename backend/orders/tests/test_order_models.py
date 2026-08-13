from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from catalogue.models import Donut
from orders.models import Order, OrderItem


class TestOrder(TestCase):
    def setUp(self) -> None:
        self.donut = Donut.objects.create(
            donut_code="THE_HOMER",
            description="Pink with sprinkles",
            price=Decimal("4.50"),
        )
        self.other_donut = Donut.objects.create(
            donut_code="THERE_IS_NO_DO_ONLY_DONUT",
            description="Yoda themed",
            price=Decimal("6.00"),
        )
        self.order = Order.objects.create()

    def test_status_defaults_to_created(self) -> None:
        """
        Setup: An order is created without a status.

        Expectations: Its status is CREATED.
        """
        assert self.order.status == Order.Status.CREATED

    def test_total_sums_the_lines(self) -> None:
        """
        Setup: An order with two lines at different prices and quantities.

        Expectations: total is the sum of quantity times unit_price.
        """
        OrderItem.objects.create(
            order=self.order,
            donut=self.donut,
            quantity=3,
            unit_price=Decimal("4.50"),
        )
        OrderItem.objects.create(
            order=self.order,
            donut=self.other_donut,
            quantity=1,
            unit_price=Decimal("6.00"),
        )

        assert self.order.total == Decimal("19.50")

    def test_quantity_must_be_greater_than_zero(self) -> None:
        """
        Setup: An order exists.

        Expectations: Adding a line with a quantity of zero raises
        IntegrityError.
        """
        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderItem.objects.create(
                order=self.order,
                donut=self.donut,
                quantity=0,
                unit_price=Decimal("4.50"),
            )
