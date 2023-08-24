from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Airport,
    Country,
    City,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Crew,
)
from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer,
    FlightSerializer,
)

FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthorizedFlightViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_list(self):
        result = self.client.get(FLIGHT_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserFlightViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        country_1 = Country.objects.create(name="Germany")
        country_2 = Country.objects.create(name="France")
        city_1 = City.objects.create(name="Berlin", country=country_1)
        city_2 = City.objects.create(name="Paris", country=country_2)
        source = Airport.objects.create(
            name="berlin Airport 1", closest_big_city=city_1
        )
        source_2 = Airport.objects.create(
            name="city Airport 3", closest_big_city=city_1
        )
        destination = Airport.objects.create(
            name="paris Airport 2", closest_big_city=city_2
        )
        route_1 = Route.objects.create(
            source=source, destination=destination, distance=590
        )
        route_2 = Route.objects.create(
            source=source_2, destination=destination, distance=440
        )
        airplane_type = AirplaneType.objects.create(name="Boing 777")
        airplane = Airplane.objects.create(
            name="test airplane", airplane_type=airplane_type, rows=38, seats_in_row=5
        )
        Flight.objects.create(
            route=route_1,
            airplane=airplane,
            departure_time="2023-10-11 20:00",
            arrival_time="2023-10-12 02:00",
        )
        Flight.objects.create(
            route=route_2,
            airplane=airplane,
            departure_time="2023-01-09 03:00",
            arrival_time="2023-01-10 12:00",
        )

        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_flight_list(self):
        result = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(flights.count(), 2)
        self.assertEqual(result.data[0]["id"], serializer.data[0]["id"])
        self.assertEqual(result.data[1]["id"], serializer.data[1]["id"])

    def test_retrieve_flight(self):
        flight = Flight.objects.get(pk=1)
        url = detail_url(flight.id)
        result = self.client.get(url)
        serializer = FlightDetailSerializer(flight)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_get_flights_filtered_by_route_source(self):
        flight_1 = Flight.objects.get(pk=1)

        result = self.client.get(FLIGHT_URL, {"route_source": f"berlin Airport"})
        serializer = FlightListSerializer([flight_1], many=True)

        self.assertEqual(serializer.data, result.data)

    def test_get_flights_filtered_by_route_destination(self):
        flight_1 = Flight.objects.get(pk=1)
        flight_2 = Flight.objects.get(pk=2)

        result = self.client.get(FLIGHT_URL, {"route_destination": f"paris Airport 2"})
        serializer = FlightListSerializer([flight_1, flight_2], many=True)

        self.assertEqual(serializer.data, result.data)

    def test_get_flights_filtered_by_departure_time(self):
        flight_1 = Flight.objects.get(pk=1)
        result = self.client.get(FLIGHT_URL, {"departure_time": f"2023-10-11"})
        serializer = FlightListSerializer([flight_1], many=True)

        self.assertEqual(serializer.data, result.data)

    def test_get_flights_filtered_by_arrival_time(self):
        flight_2 = Flight.objects.get(pk=2)
        result = self.client.get(FLIGHT_URL, {"arrival_time": f"2023-01-10"})
        serializer = FlightListSerializer([flight_2], many=True)

        self.assertEqual(serializer.data, result.data)

    def test_create_flight_forbidden(self):
        route = Route.objects.get(pk=1)
        airplane = Airplane.objects.get(pk=1)
        crew = Crew.objects.create(first_name="John", last_name="Smith")
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-12-13 19:00",
            "arrival_time": "2023-10-14 01:00",
            "crew": [crew.id],
        }
        result = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_forbidden(self):
        flight = Flight.objects.get(pk=1)
        route = Route.objects.get(pk=2)
        airplane = Airplane.objects.get(pk=1)
        crew = Crew.objects.create(first_name="John", last_name="Smith")
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-12-13 19:00",
            "arrival_time": "2023-10-14 01:00",
            "crew": [crew.id],
        }

        url = detail_url(flight.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_forbidden(self):
        flight = Flight.objects.get(pk=1)
        url = detail_url(flight.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightViewSetTest(TestCase):
    def setUp(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@email.com", password="password"
        )
        country_1 = Country.objects.create(name="Germany")
        country_2 = Country.objects.create(name="France")
        city_1 = City.objects.create(name="Berlin", country=country_1)
        city_2 = City.objects.create(name="Paris", country=country_2)
        source = Airport.objects.create(
            name="berlin Airport 1", closest_big_city=city_1
        )
        destination = Airport.objects.create(
            name="paris Airport 2", closest_big_city=city_2
        )
        route_1 = Route.objects.create(
            source=source, destination=destination, distance=590
        )
        airplane_type = AirplaneType.objects.create(name="Boing 777")
        airplane = Airplane.objects.create(
            name="test airplane", airplane_type=airplane_type, rows=38, seats_in_row=5
        )
        Flight.objects.create(
            route=route_1,
            airplane=airplane,
            departure_time="2023-10-11 20:00",
            arrival_time="2023-10-12 02:00",
        )
        self.client = APIClient()
        self.client.force_authenticate(admin)

    def test_create_flight(self):
        route = Route.objects.get(pk=1)
        airplane = Airplane.objects.get(pk=1)
        crew = Crew.objects.create(first_name="John", last_name="Smith")
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-12-13 19:00",
            "arrival_time": "2023-12-14 01:00",
            "crew": [crew.id],
        }
        result = self.client.post(FLIGHT_URL, payload)
        new_flight = Flight.objects.get(id=result.data["id"])
        serializer = FlightSerializer(new_flight)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data, result.data)

    def test_update_flight(self):
        route = Route.objects.get(pk=1)
        airplane = Airplane.objects.get(pk=1)
        crew = Crew.objects.create(first_name="John", last_name="Smith")
        flight = Flight.objects.get(pk=1)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-12-28 19:00",
            "arrival_time": "2023-12-29 01:00",
            "crew": [crew.id],
        }

        url = detail_url(flight.id)
        result = self.client.put(url, payload)

        serializer = FlightSerializer(route, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_delete_flight(self):
        flight = Flight.objects.get(pk=1)
        url = detail_url(flight.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

    def test_arrival_date_validation(self):
        route = Route.objects.get(pk=1)
        airplane = Airplane.objects.get(pk=1)
        crew = Crew.objects.create(first_name="John", last_name="Smith")
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-10-13 19:00",
            "arrival_time": "2023-10-05 01:00",
            "crew": [crew.id],
        }
        result = self.client.post(FLIGHT_URL, payload)
        serializer = FlightSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result.data,
            {"arrival_time": ["arrival time can not be less than departure time"]},
        )
