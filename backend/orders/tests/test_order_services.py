from decimal import Decimal

from django.test import TestCase

from catalogue.models import Donut
from orders.exceptions import (
    DonutNotFound,
    DonutUnavailable,
    InvalidQuantity,
    InvalidOrder,
    InvalidStatusChange,
)
from orders.models import Order
from orders.services import (
    create_order,
    dispatch_order,
)


class TestCreateOrder(TestCase):
    def setUp(self) -> None:
        self.homer = Donut.objects.create(
            donut_code="THE_HOMER",
            description="Pink with sprinkles",
            price=Decimal("4.50"),
        )
        self.yoda = Donut.objects.create(
            donut_code="THERE_IS_NO_DO_ONLY_DONUT",
            description="Yoda themed",
            price=Decimal("6.00"),
        )

    def test_creates_an_order_with_its_lines(self) -> None:
        """
        Setup: Two available donuts and a payload selecting both.

        Expectations: An Order is persisted with a line per selection.
        """
        order = create_order(
            [
                {"donut_code": self.homer.donut_code, "quantity": 3},
                {"donut_code": self.yoda.donut_code, "quantity": 1},
            ]
        )

        assert Order.objects.count() == 1
        assert order.items.count() == 2
        assert order.status == Order.Status.CREATED

        line = order.items.get(donut=self.homer)
        assert line.quantity == 3
        assert line.unit_price == Decimal("4.50")

    def test_total_reflects_every_line(self) -> None:
        """
        Setup: Three donuts at 4.50 and one at 6.00.

        Expectations: The order's total is 19.50.
        """
        order = create_order(
            [
                {"donut_code": self.homer.donut_code, "quantity": 3},
                {"donut_code": self.yoda.donut_code, "quantity": 1},
            ]
        )

        assert order.total == Decimal("19.50")

    def test_merges_duplicate_donut_codes(self) -> None:
        """
        Setup: A payload naming the same donut_code twice, quantities 2 and 3.

        Expectations: The order has one line for that donut with a quantity
        of 5.
        """
        order = create_order(
            [
                {"donut_code": self.homer.donut_code, "quantity": 2},
                {"donut_code": self.homer.donut_code, "quantity": 3},
            ]
        )

        line = order.items.get(donut=self.homer)
        assert line.quantity == 5

    def test_rejects_an_unknown_donut_code(self) -> None:
        """
        Setup: A payload naming a donut_code that does not exist.

        Expectations: Rejected, and no order is persisted.
        """
        with self.assertRaises(DonutNotFound):
            create_order([{"donut_code": "Glazed and Confused", "quantity": 2}])

    def test_rejects_an_unavailable_donut(self) -> None:
        """
        Setup: A donut with available set to False.

        Expectations: Rejected, and no order is persisted.
        """
        self.homer.available = False

        with self.assertRaises(DonutUnavailable):
            create_order([{"donut_code": self.homer.donut_code, "quantity": 2}])

    def test_rejects_a_quantity_of_zero_or_less(self) -> None:
        """
        Setup: A payload with a quantity of zero.

        Expectations: Rejected, and no order is persisted.
        """
        with self.assertRaises(InvalidQuantity):
            create_order([{"donut_code": self.homer.donut_code, "quantity": 0}])

    def test_rejects_an_empty_item_list(self) -> None:
        """
        Setup: A payload with no donuts in it.

        Expectations: Rejected, and no order is persisted.
        """
        with self.assertRaises(InvalidOrder):
            create_order([])

    def test_persists_nothing_when_one_line_is_invalid(self) -> None:
        """
        Setup: A payload with one valid selection and one unknown code.

        Expectations: Rejected, and neither the order nor the valid line
        survives.
        """
        order = create_order(
            [
                {"donut_code": self.homer.donut_code, "quantity": 2},
                {"donut_code": "UNKNOWN DONUT", "quantity": 3},
            ]
        )

        assert Order.objects.count() == 0

        line = order.items.get(donut=self.homer)
        assert len(line) == 0


class TestDispatchOrder(TestCase):
    def setUp(self) -> None:
        self.order = Order.objects.create()

    def test_moves_a_created_order_to_dispatched(self) -> None:
        """
        Setup: An order in CREATED.

        Expectations: Its status becomes DISPATCHED and is persisted.
        """
        dispatch_order(self.order)

        self.order.refresh_from_db()
        assert self.order.status == Order.Status.DISPATCHED

    def test_rejects_an_order_that_is_already_dispatched(self) -> None:
        """
        Setup: An order in DISPATCHED.

        Expectations: Rejected, and the status is unchanged.
        """
        self.order.status = Order.Status.DISPATCHED
        self.order.save()

        with self.assertRaises(InvalidStatusChange):
            dispatch_order(self.order)

        self.order.refresh_from_db()
        assert self.order.status == Order.Status.DISPATCHED
