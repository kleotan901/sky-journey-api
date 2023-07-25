from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Crew,
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class CrewSerializer(serializers.ModelSerializer):
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["id", "full_name"]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "country"]


class CityListSerializer(CitySerializer):
    country = serializers.CharField(source="country.name")

    class Meta:
        model = City
        fields = ["id", "name", "country"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ["source", "destination"]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "route",
            "departure_time",
            "arrival_time",
        ]


class FlightListSerializer(FlightSerializer):
    route = RouteSerializer(read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time"]


class FlightDetailSerializer(FlightListSerializer):
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["flight"], attrs["row"], "row", "rows", serializers.ValidationError
        )
        Ticket.validate_seat(
            attrs["flight"],
            attrs["seat"],
            "seat",
            "seats_in_row",
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
        ]


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
