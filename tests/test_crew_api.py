from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewSerializer, CrewListSerializer

CREW_URL = reverse("airport:crew-list")


def detail_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])


class UnauthorizedUserCrewViewSetTest(TestCase):
    def setUp(self) -> None:
        Crew.objects.create(first_name="John", last_name="Smith")
        self.client = APIClient()

    def test_get_crew_list(self):
        result = self.client.get(CREW_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_member_of_crew(self):
        member_of_crew = Crew.objects.get(pk=1)
        result = self.client.get(detail_url(member_of_crew.id))
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserCrewViewSetTest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        Crew.objects.create(first_name="John", last_name="Smith")
        Crew.objects.create(first_name="Bob", last_name="Muller")
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_crew_list(self):
        members_of_crew = Crew.objects.all()
        result = self.client.get(CREW_URL)
        serializer = CrewListSerializer(members_of_crew, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(members_of_crew.count(), 2)

    def test_retrieve_member_of_crew(self):
        member_of_crew = Crew.objects.get(pk=1)
        result = self.client.get(detail_url(member_of_crew.id))
        serializer = CrewSerializer(member_of_crew)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_member_of_crew_forbidden(self):
        payload = {
            "first_name": "test first name",
            "last_name": "test last name",
        }

        result = self.client.post(CREW_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_member_of_crew_forbidden(self):
        member_of_crew = Crew.objects.get(pk=1)
        payload = {
            "first_name": "test first name",
            "last_name": "test last name",
        }
        url = detail_url(member_of_crew.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_member_of_crew_forbidden(self):
        crew = Crew.objects.get(pk=1)
        url = detail_url(crew.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewViewSetTest(TestCase):
    def setUp(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@email.com", password="password"
        )
        Crew.objects.create(first_name="John", last_name="Smith")
        Crew.objects.create(first_name="Bob", last_name="Muller")
        self.client = APIClient()
        self.client.force_authenticate(admin)

    def test_create_member_of_crew(self):
        payload = {
            "first_name": "test first name",
            "last_name": "test last name",
        }
        result = self.client.post(CREW_URL, payload)

        new_member = Crew.objects.get(last_name="test last name")
        serializer = CrewListSerializer(new_member)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            serializer.data["full_name"],
            f"{result.data['first_name']} {result.data['last_name']}",
        )
        for key in payload:
            self.assertEqual(payload[key], getattr(new_member, key))

    def test_update_member_of_crew(self):
        member_of_crew = Crew.objects.get(pk=1)
        payload = {
            "first_name": "new first name",
            "last_name": "test last name",
        }
        url = detail_url(member_of_crew.id)
        result = self.client.put(url, payload)

        serializer = CrewSerializer(member_of_crew, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(member_of_crew.first_name, "new first name")
        self.assertEqual(result.data, serializer.data)

    def test_delete_member_of_crew(self):
        crew = Crew.objects.get(pk=1)
        url = detail_url(crew.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
