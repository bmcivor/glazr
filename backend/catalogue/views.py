from django.db.models import Q, QuerySet
from rest_framework import mixins, viewsets

from catalogue.models import Donut
from catalogue.serializers import DonutSerializer
from glazr.messaging import publish_event


class DonutViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read and write access to the donut catalogue.

    Composed from mixins rather than ModelViewSet so that delete is not
    exposed.

    Requirements do not suggest to expose a delete function.
    """

    serializer_class = DonutSerializer
    queryset = Donut.objects.all()

    def get_queryset(self) -> QuerySet[Donut]:
        queryset = super().get_queryset()

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(donut_code__icontains=search) | Q(description__icontains=search)
            )

        available = self.request.query_params.get("available")
        if available is not None:
            queryset = queryset.filter(available=available.lower() == "true")

        return queryset

    def perform_create(self, serializer: DonutSerializer) -> None:
        donut = serializer.save()
        publish_event(
            "donut.created",
            {"donut_id": donut.id, "donut_code": donut.donut_code},
        )

    def perform_update(self, serializer: DonutSerializer) -> None:
        donut = serializer.save()
        publish_event(
            "donut.updated",
            {"donut_id": donut.id, "donut_code": donut.donut_code},
        )
