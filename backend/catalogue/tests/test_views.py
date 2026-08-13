from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalogue.models import Donut


class TestDonutAPI(APITestCase):
    def setUp(self) -> None:
        self.donut_code = "THE_HOMER"
        self.description = "Pink with sprinkles"
        self.price = "4.50"
        self.donut = Donut.objects.create(
            donut_code=self.donut_code,
            description=self.description,
            price=self.price,
        )
        self.list_url = reverse("donut-list")
        self.detail_url = reverse("donut-detail", args=[self.donut.id])

    def test_retrieve(self) -> None:
        """
        Setup: A donut exists.

        Expectations: The detail endpoint returns that donut.
        """
        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["donut_code"] == self.donut_code
        assert response.data["price"] == self.price

    def test_list__returns_donuts(self) -> None:
        """
        Setup: One donut exists.

        Expectations: The list endpoint returns it, with price as a decimal
        string.
        """
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["donut_code"] == self.donut_code
        assert response.data[0]["price"] == self.price

    def test_list__filters_on_search(self) -> None:
        """
        Setup: Two donuts exist with different codes.

        Expectations: Searching narrows the list to the matching donut.
        """
        Donut.objects.create(
            donut_code="THERE_IS_NO_DO_ONLY_DONUT",
            description="Yoda themed",
            price="6.00",
        )

        response = self.client.get(self.list_url, {"search": "HOMER"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["donut_code"] == self.donut_code

    def test_list__filters_on_available(self) -> None:
        """
        Setup: One available donut and one unavailable donut.

        Expectations: Filtering on available excludes the unavailable one.
        """
        Donut.objects.create(
            donut_code="SOLD_OUT",
            description="None left",
            price="3.00",
            available=False,
        )

        response = self.client.get(self.list_url, {"available": "true"})

        assert len(response.data) == 1
        assert response.data[0]["donut_code"] == self.donut_code

    def test_create(self) -> None:
        """
        Setup: A payload for a donut that does not exist yet.

        Expectations: It is created and returned with 201.
        """
        response = self.client.post(
            self.list_url,
            {
                "donut_code": "THERE_IS_NO_DO_ONLY_DONUT",
                "description": "Yoda themed",
                "price": "6.00",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Donut.objects.count() == 2

    def test_create__rejects_duplicate_donut_code(self) -> None:
        """
        Setup: A donut exists with the code THE_HOMER.

        Expectations: Creating another with the same code returns 400 and
        nothing is created.
        """
        response = self.client.post(
            self.list_url,
            {
                "donut_code": self.donut_code,
                "description": "Duplicate",
                "price": "5.00",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "donut_code" in response.data
        assert Donut.objects.count() == 1

    def test_update(self) -> None:
        """
        Setup: A payload for a donut that already exists. Modify a field
        on the payload. Update donut.

        Expectations: The existing Donut record is updated.
        """
        response = self.client.patch(self.detail_url, {"price": "9.00"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "9.00"

        self.donut.refresh_from_db()
        assert self.donut.price == Decimal("9.00")

    def test_update__rejects_duplicate_donut_code(self) -> None:
        """
        Setup: Two donuts exist with different codes.

        Expectations: Changing the second donut's code to the first's returns
        400 and leaves it unchanged.
        """
        other = Donut.objects.create(
            donut_code="SOLD_OUT", description="None left", price="3.00"
        )

        response = self.client.patch(
            reverse("donut-detail", args=[other.id]),
            {"donut_code": self.donut_code},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        other.refresh_from_db()
        assert other.donut_code == "SOLD_OUT"
