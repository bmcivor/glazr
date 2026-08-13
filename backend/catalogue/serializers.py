from rest_framework import serializers

from catalogue.models import Donut


class DonutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donut
        fields = ["id", "donut_code", "description", "price", "available"]
