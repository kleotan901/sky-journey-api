from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Country, City, Route
from airport.serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
)

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class UnauthorizedRouteViewSetTest(TestCase):
    def setUp(self):
        country = Country.objects.create(name="test country")
        city_1 = City.objects.create(name="Test City", country=country)
        city_2 = City.objects.create(name="Test City", country=country)
        source = Airport.objects.create(name="Test Airport 1", closest_big_city=city_1)
        destination = Airport.objects.create(
            name="Test Airport 2", closest_big_city=city_2
        )
        Route.objects.create(source=source, destination=destination, distance=590)
        self.client = APIClient()

    def test_route_list(self):
        result = self.client.get(ROUTE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airport(self):
        url = detail_url(route_id=1)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserRouteViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        get_user_model().objects.create_user(
            email="test_2@email.com", password="password"
        )
        country_1 = Country.objects.create(name="country 1")
        country_2 = Country.objects.create(name="country 2")
        city_1 = City.objects.create(name="City 1", country=country_1)
        city_2 = City.objects.create(name="City 2", country=country_2)
        city_3 = City.objects.create(name="City 3", country=country_1)
        source_1 = Airport.objects.create(name="Airport 1", closest_big_city=city_1)
        destination = Airport.objects.create(name="Airport 2", closest_big_city=city_2)
        source_2 = Airport.objects.create(name="Airport 3", closest_big_city=city_3)
        Route.objects.create(source=source_1, destination=destination, distance=490)
        Route.objects.create(source=source_2, destination=destination, distance=550)

        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_route_list(self):
        result = self.client.get(ROUTE_URL)
        routs = Route.objects.all()
        serializer = RouteListSerializer(routs, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(routs.count(), 2)

    def test_retrieve_route(self):
        route = Route.objects.get(pk=1)
        url = detail_url(route.id)
        result = self.client.get(url)
        serializer = RouteDetailSerializer(route)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_get_routes_filtered_by_source(self):
        route_1 = Route.objects.get(pk=1)

        result = self.client.get(ROUTE_URL, {"source": f"Airport 1"})
        serializer = RouteListSerializer(route_1)

        self.assertIn(serializer.data, result.data)

    def test_get_routes_filtered_by_destination(self):
        route_1 = Route.objects.get(pk=1)
        route_2 = Route.objects.get(pk=2)

        result = self.client.get(ROUTE_URL, {"destination": f"Airport 2"})
        serializer = RouteListSerializer([route_1, route_2], many=True)

        self.assertEqual(serializer.data, result.data)

    def test_create_route_forbidden(self):
        source = Airport.objects.get(pk=1)
        destination = Airport.objects.get(pk=2)
        payload = {"source": source.id, "destination": destination.id, "distance": 350}

        result = self.client.post(ROUTE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        source = Airport.objects.get(pk=1)
        destination = Airport.objects.get(pk=2)
        route = Route.objects.get(pk=1)
        url = detail_url(route.id)
        payload = {"source": source.id, "destination": destination.id, "distance": 1150}

        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_forbidden(self):
        route = Route.objects.get(pk=1)
        url = detail_url(route.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteViewSetTest(TestCase):
    def setUp(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@email.com", password="password"
        )
        country_1 = Country.objects.create(name="country 1")
        country_2 = Country.objects.create(name="country 2")
        city_1 = City.objects.create(name="City 1", country=country_1)
        city_2 = City.objects.create(name="City 2", country=country_2)
        source_1 = Airport.objects.create(name="Airport 1", closest_big_city=city_1)
        destination = Airport.objects.create(name="Airport 2", closest_big_city=city_2)
        Route.objects.create(source=source_1, destination=destination, distance=490)
        self.client = APIClient()
        self.client.force_authenticate(admin)

    def test_create_route(self):
        source = Airport.objects.get(pk=1)
        destination = Airport.objects.get(pk=1)
        payload = {"source": source.id, "destination": destination.id, "distance": 460}
        result = self.client.post(ROUTE_URL, payload)
        new_route = Route.objects.get(id=result.data["id"])

        serializer = RouteSerializer(new_route)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data, result.data)

    def test_update_route(self):
        source = Airport.objects.get(pk=1)
        destination = Airport.objects.get(pk=1)
        route = Route.objects.get(pk=1)
        old_distance = route.distance
        payload = {"source": source.id, "destination": destination.id, "distance": 560}

        url = detail_url(route.id)
        result = self.client.put(url, payload)

        serializer = RouteSerializer(route, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_distance, route.distance)
        self.assertEqual(result.data, serializer.data)

    def test_delete_route(self):
        route = Route.objects.get(pk=1)
        url = detail_url(route.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
