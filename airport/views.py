from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from airport.models import (
    Crew,
    Country,
    City,
    Airplane,
    AirplaneType,
    Airport,
    Route,
    Flight,
    Order,
)
from airport.serializers import (
    CrewSerializer,
    CountrySerializer,
    CitySerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    RouteSerializer,
    FlightSerializer,
    OrderSerializer,
    RouteListSerializer,
    CityListSerializer,
    AirplaneListSerializer,
    AirportListSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderListSerializer,
)
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related("country")
    serializer_class = CityListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CitySerializer
        return CityListSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirplaneSerializer
        return AirplaneListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.select_related("closest_big_city__country")
    serializer_class = AirportListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirportSerializer
        return AirportListSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return RouteSerializer
        return RouteListSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane"
    )
    serializer_class = FlightListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return FlightSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset.prefetch_related(
            "tickets__flight__route", "tickets__flight__airplane"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return OrderSerializer

        return OrderListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
