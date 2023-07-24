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
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


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
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time"]


class FlightDetailSerializer(FlightListSerializer):
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "row",
            "seat",
            "flight",
        ]
