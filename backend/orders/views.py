from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from orders.exceptions import OrderError
from orders.models import Order
from orders.serializers import CreateOrderSerializer, OrderSerializer
from orders.services import create_order, dispatch_order


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Orders placed over HTTP.

    Creation and dispatch both delegate to the service layer, so the rules are
    identical to the ones the message consumer gets.
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related("items__donut")

    def create(self, request: Request) -> Response:
        payload = CreateOrderSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        try:
            order = create_order(payload.validated_data["donuts"])
        except OrderError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="dispatch")
    def mark_dispatched(self, request: Request, pk: str | None = None) -> Response:
        order = self.get_object()

        try:
            dispatch_order(order)
        except OrderError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data)
