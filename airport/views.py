from rest_framework import viewsets

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


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related("country")
    serializer_class = CityListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CitySerializer
        return CityListSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirplaneSerializer
        return AirplaneListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.select_related("closest_big_city__country")
    serializer_class = AirportListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirportSerializer
        return AirportListSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return RouteSerializer
        return RouteListSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane"
    )
    serializer_class = FlightListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return FlightSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets__flight")
    serializer_class = OrderListSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderSerializer

        return OrderListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
