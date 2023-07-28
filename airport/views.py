from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

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
    CrewListSerializer,
    RouteDetailSerializer,
)
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related("country")
    serializer_class = CityListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the city with filters by name"""
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = City.objects.filter(name__icontains=name)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CitySerializer
        return CityListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by name of city (ex. ?name=name)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the airplane filtering by name"""
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = Airplane.objects.filter(name__icontains=name)
        return queryset

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

    def get_queryset(self):
        """Retrieve the airports filtering by closest big city"""
        queryset = self.queryset
        closest_big_city = self.request.query_params.get("closest_big_city")
        if closest_big_city:
            queryset = Airport.objects.filter(
                closest_big_city__name__icontains=closest_big_city
            )
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="closest_big_city",
                description="Filter by name of closest big city (ex. ?closest_big_city=closest_big_city)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the routs filtering by source, destination"""
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        if source:
            queryset = Route.objects.filter(source__name__icontains=source)
        if destination:
            queryset = Route.objects.filter(destination__name__icontains=destination)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return RouteSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by the name of the departure airport (ex. ?source=London Heathrow)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by the name of the arrival airport (ex. ?destination=London Heathrow)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane"
    )
    serializer_class = FlightListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the flights filtering by route, departure time and arrival time"""
        queryset = self.queryset
        route_destination = self.request.query_params.get("route_destination")
        route_source = self.request.query_params.get("route_source")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")
        if self.action == "list":
            queryset = (
                queryset.select_related("airplane").annotate(
                    tickets_available=F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")
        if route_destination:
            queryset = Flight.objects.filter(
                route__destination__name__icontains=route_destination
            )
        if route_source:
            queryset = Flight.objects.filter(
                route__source__name__icontains=route_source
            )
        if departure_time:
            queryset = Flight.objects.filter(departure_time__icontains=departure_time)
        if arrival_time:
            queryset = Flight.objects.filter(arrival_time__icontains=arrival_time)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return FlightSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="route_destination",
                description=(
                    "Filter by the arrival airport (ex. ?route_destination=Los Angeles International)"
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="route_source",
                description=(
                    "Filter by the arrival airport (ex. ?route_source=Los Angeles International)"
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="departure_time",
                description="Filter by the departure_time (ex. ?departure_time=2023-10-11)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="arrival_time",
                description="Filter by the arrival_time (ex. ?arrival_time=2023-10-12)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderSerializer

        return OrderListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
