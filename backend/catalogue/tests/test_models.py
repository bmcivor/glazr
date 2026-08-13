from django.db import IntegrityError, transaction
from django.test import TestCase

from catalogue.models import Donut


class TestDonut(TestCase):
    def setUp(self) -> None:
        self.donut_code = "THE_HOMER"
        self.description = "Pink with sprinkles"
        self.price = "4.50"

    def test_donut_code_is_unique(self) -> None:
        """
        Setup: A donut exists with the code THE_HOMER.

        Expectations: Creating a second donut with the same code raises
        IntegrityError.
        """
        Donut.objects.create(
            donut_code=self.donut_code,
            description=self.description,
            price=self.price,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Donut.objects.create(
                donut_code=self.donut_code,
                description="Duplicate",
                price="5.00",
            )
