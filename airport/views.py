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
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CityListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CitySerializer
        return CityListSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirplaneSerializer
        return AirplaneListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirportSerializer
        return AirportListSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return RouteSerializer
        return RouteListSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return FlightSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
