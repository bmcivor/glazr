from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    donut_code = serializers.CharField(source="donut.donut_code", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["donut_code", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "created_at", "items", "total"]


class OrderSelectionSerializer(serializers.Serializer):
    donut_code = serializers.CharField()
    quantity = serializers.IntegerField()


class CreateOrderSerializer(serializers.Serializer):
    donuts = OrderSelectionSerializer(many=True)
