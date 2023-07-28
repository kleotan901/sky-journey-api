from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Country, City
from airport.serializers import AirportListSerializer, AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")


def detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


class UnauthorizedAirportViewSetTest(TestCase):
    def setUp(self):
        country = Country.objects.create(name="test country")
        city = City.objects.create(name="Test City", country=country)
        Airport.objects.create(name="Test Airport", closest_big_city=city)
        self.client = APIClient()

    def test_get_airport_list(self):
        result = self.client.get(AIRPORT_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airport(self):
        url = detail_url(airport_id=1)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserAirportViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        country_1 = Country.objects.create(name="Germany")
        country_2 = Country.objects.create(name="France")
        city_1 = City.objects.create(name="Berlin", country=country_1)
        city_2 = City.objects.create(name="Paris", country=country_2)
        Airport.objects.create(name="berlin Airport 1", closest_big_city=city_1)
        Airport.objects.create(name="paris Airport 2", closest_big_city=city_2)
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_airport_list(self):
        result = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(airports.count(), 2)

    def test_retrieve_airport(self):
        airport = Airport.objects.get(pk=1)
        url = detail_url(airport.id)
        result = self.client.get(url)
        serializer = AirportListSerializer(airport)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_get_airports_filtered_by_closest_big_city(self):
        test_airport = Airport.objects.get(pk=1)

        result = self.client.get(AIRPORT_URL, {"closest_big_city": "Berlin"})
        serializer = AirportListSerializer(test_airport)

        self.assertIn(serializer.data, result.data)

    def test_create_airport_forbidden(self):
        city = City.objects.get(pk=1)
        payload = {"name": "Sample Airport", "closest_big_city": city}

        result = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airport_forbidden(self):
        city = City.objects.get(pk=1)
        airport = Airport.objects.get(pk=1)
        payload = {"name": "updated Airport", "closest_big_city": city}
        url = detail_url(airport.id)

        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airport_forbidden(self):
        airport = Airport.objects.get(pk=1)
        url = detail_url(airport.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportViewSetTest(TestCase):
    def setUp(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@email.com", password="password"
        )
        country_1 = Country.objects.create(name="Germany")
        country_2 = Country.objects.create(name="France")
        city_1 = City.objects.create(name="Berlin", country=country_1)
        city_2 = City.objects.create(name="Paris", country=country_2)
        Airport.objects.create(name="berlin Airport 1", closest_big_city=city_1)
        Airport.objects.create(name="paris Airport 2", closest_big_city=city_2)
        self.client = APIClient()
        self.client.force_authenticate(admin)

    def test_create_airport(self):
        city = City.objects.get(pk=1)
        payload = {"name": "Sample Airport", "closest_big_city": city.id}

        result = self.client.post(AIRPORT_URL, payload)

        new_airport = Airport.objects.get(id=result.data["id"])

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(new_airport.name, "Sample Airport")

    def test_update_airport(self):
        city = City.objects.get(pk=1)
        airport = Airport.objects.get(pk=1)
        payload = {"name": "London Airport", "closest_big_city": city.id}

        url = detail_url(airport.id)
        result = self.client.put(url, payload)

        serializer = AirportSerializer(airport, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(airport.name, "London Airport")
        self.assertEqual(result.data, serializer.data)

    def test_delete_airport(self):
        airport = Airport.objects.get(pk=1)
        url = detail_url(airport.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
