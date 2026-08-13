from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalogue.models import Donut
from orders.models import Order
from orders.services import create_order, dispatch_order


class TestOrderAPI(APITestCase):
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
        self.list_url = reverse("order-list")

    def test_create(self) -> None:
        """
        Setup: A payload selecting two available donuts.

        Expectations: 201, and the body carries the order id, status, its
        lines and the server-calculated total.
        """
        response = self.client.post(
            self.list_url,
            {
                "donuts": [
                    {"donut_code": self.homer.donut_code, "quantity": 3},
                    {"donut_code": self.yoda.donut_code, "quantity": 1},
                ]
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == Order.Status.CREATED
        assert response.data["total"] == "19.50"
        assert len(response.data["items"]) == 2
        assert Order.objects.count() == 1

    def test_create__rejects_an_unknown_donut_code(self) -> None:
        """
        Setup: A payload naming a donut_code that does not exist.

        Expectations: 400 naming the offending code, and no order persisted.
        """
        response = self.client.post(
            self.list_url,
            {"donuts": [{"donut_code": "Hole Lotta Love", "quantity": 1}]},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No donut with code Hole Lotta Love." == response.data["detail"]
        assert Order.objects.count() == 0

    def test_create__rejects_an_unavailable_donut(self) -> None:
        """
        Setup: A payload selecting a donut with available set to False.

        Expectations: 400, and no order persisted.
        """
        response = self.client.post(
            self.list_url,
            {"donuts": [{"donut_code": "Hole Lotta Love", "quantity": 1}]},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No donut with code Hole Lotta Love." == response.data["detail"]
        assert Order.objects.count() == 0

    def test_create__rejects_a_quantity_of_zero(self) -> None:
        """
        Setup: A payload with a quantity of zero.

        Expectations: 400, and no order persisted.
        """
        response = self.client.post(
            self.list_url,
            {"donuts": [{"donut_code": "Hole Lotta Love", "quantity": 0}]},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Quantity for Hole Lotta Love must be greater than zero."
            == response.data["detail"]
        )
        assert Order.objects.count() == 0

    def test_list(self) -> None:
        """
        Setup: Two orders exist.

        Expectations: Both are returned, each with its lines and total.
        """
        create_order([{"donut_code": self.homer.donut_code, "quantity": 3}])
        create_order([{"donut_code": self.yoda.donut_code, "quantity": 2}])

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        totals = {order["total"] for order in response.data}
        assert totals == {"13.50", "12.00"}

        for order in response.data:
            assert len(order["items"]) == 1

    def test_retrieve(self) -> None:
        """
        Setup: An order exists.

        Expectations: The detail endpoint returns it with its lines and
        total.
        """
        order = create_order([{"donut_code": self.homer.donut_code, "quantity": 3}])

        response = self.client.get(reverse("order-detail", args=[order.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(order.id)
        assert response.data["total"] == "13.50"
        assert len(response.data["items"]) == 1
        assert response.data["items"][0]["donut_code"] == self.homer.donut_code

    def test_dispatch(self) -> None:
        """
        Setup: An order in CREATED.

        Expectations: 200, status is DISPATCHED, and the change is persisted.
        """
        order = create_order([{"donut_code": self.homer.donut_code, "quantity": 1}])

        response = self.client.post(reverse("order-mark-dispatched", args=[order.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == Order.Status.DISPATCHED

        order.refresh_from_db()
        assert order.status == Order.Status.DISPATCHED

    def test_dispatch__rejects_an_already_dispatched_order(self) -> None:
        """
        Setup: An order already in DISPATCHED.

        Expectations: 400, and the status is unchanged.
        """
        order = create_order([{"donut_code": self.homer.donut_code, "quantity": 1}])
        dispatch_order(order)

        response = self.client.post(reverse("order-mark-dispatched", args=[order.id]))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        order.refresh_from_db()
        assert order.status == Order.Status.DISPATCHED
