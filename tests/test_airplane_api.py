from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import (
    AirplaneSerializer,
    AirplaneListSerializer,
)

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthorizedUserAirplaneViewSetTest(TestCase):
    def setUp(self):
        airplane_type = AirplaneType.objects.create(name="Boing 737")
        Airplane.objects.create(
            name="Greenbird", rows=45, seats_in_row=6, airplane_type=airplane_type
        )
        self.client = APIClient()

    def test_airplane_list(self):
        result = self.client.get(AIRPLANE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airplane(self):
        url = detail_url(airplane_id=1)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserAirplaneViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        airplane_type = AirplaneType.objects.create(name="Boing 737")
        Airplane.objects.create(
            rows=45, seats_in_row=6, name="Greybird", airplane_type=airplane_type
        )
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_airplane_list(self):
        result = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(airplanes.count(), 1)

    def test_get_airplanes_filtered_by_name(self):
        airplane_type = AirplaneType.objects.get(pk=1)
        airplane_1 = Airplane.objects.create(
            name="Whitebird", rows=39, seats_in_row=4, airplane_type=airplane_type
        )
        airplane_2 = Airplane.objects.create(
            name="Sample Airplane", rows=39, seats_in_row=4, airplane_type=airplane_type
        )
        result = self.client.get(AIRPLANE_URL, {"name": "Sample"})
        serializer = AirplaneListSerializer(airplane_2)
        serializer_2 = AirplaneSerializer(airplane_1)

        self.assertIn(serializer.data, result.data)
        self.assertNotIn(serializer_2.data, result.data)

    def test_retrieve_airplane(self):
        airplane = Airplane.objects.get(pk=1)
        url = detail_url(airplane.id)
        result = self.client.get(url)
        serializer = AirplaneListSerializer(airplane)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.get(pk=1)
        payload = {
            "name": "new name",
            "rows": 100,
            "seats_in_row": 9,
            "airplane_type": airplane_type,
        }

        result = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_forbidden(self):
        airplane = Airplane.objects.get(pk=1)
        airplane_type = AirplaneType.objects.get(pk=1)
        payload = {
            "name": "update airplane",
            "rows": 100,
            "seats_in_row": 9,
            "airplane_type": airplane_type,
        }
        url = detail_url(airplane_id=airplane.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        airplane = Airplane.objects.get(pk=1)
        url = detail_url(airplane.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneViewSetTest(TestCase):
    def setUp(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@email.com", password="password"
        )
        airplane_type = AirplaneType.objects.create(name="Boing 737")
        Airplane.objects.create(
            name="Greenbird", rows=45, seats_in_row=6, airplane_type=airplane_type
        )
        self.client = APIClient()
        self.client.force_authenticate(admin)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.get(pk=1)
        payload = {
            "name": "new airplane",
            "rows": 98,
            "seats_in_row": 9,
            "airplane_type": airplane_type.id,
        }

        result = self.client.post(AIRPLANE_URL, payload)
        new_airplane = Airplane.objects.get(id=result.data["id"])

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(new_airplane.name, "new airplane")

    def test_update_airplane(self):
        airplane_type = AirplaneType.objects.get(pk=1)
        airplane = Airplane.objects.get(pk=1)
        payload = {
            "name": "updated airplane",
            "rows": 98,
            "seats_in_row": 9,
            "airplane_type": airplane_type.id,
        }
        url = detail_url(airplane.id)
        result = self.client.put(url, payload)

        serializer = AirplaneSerializer(airplane, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(airplane.name, "updated airplane")
        self.assertEqual(result.data, serializer.data)

    def test_delete_airplane(self):
        airplane = Airplane.objects.get(pk=1)
        url = detail_url(airplane.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
