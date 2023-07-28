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
    Ticket,
    Order,
)
from airport.serializers import OrderListSerializer, OrderSerializer

ORDER_URL = reverse("airport:order-list")


def detail_url(order_id):
    return reverse("airport:order-detail", args=[order_id])


class UnauthorizedOrderViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_order_list(self):
        result = self.client.get(ORDER_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserOrderViewSetTest(TestCase):
    def setUp(self):
        owner = get_user_model().objects.create_user(
            email="owner@email.com", password="password"
        )
        get_user_model().objects.create_user(
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
        flight_1 = Flight.objects.create(
            route=route_1,
            airplane=airplane,
            departure_time="2023-10-11 20:00",
            arrival_time="2023-10-12 02:00",
        )
        order = Order.objects.create(created_at="2023-07-26 10:50", user=owner)
        Ticket.objects.create(row=20, seat=4, flight=flight_1, order=order)
        Ticket.objects.create(row=20, seat=3, flight=flight_1, order=order)

        self.client = APIClient()
        self.client.force_authenticate(owner)

    def test_get_order_list_if_owner(self):
        owner = get_user_model().objects.get(pk=1)

        result = self.client.get(ORDER_URL)
        orders = Order.objects.filter(user=owner)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(orders.count(), 1)
        self.assertEqual(result.data, serializer.data)

    def test_get_order_list_if_not_owner(self):
        owner = get_user_model().objects.get(pk=1)
        user = get_user_model().objects.get(pk=2)
        self.client.force_authenticate(user)

        result = self.client.get(ORDER_URL)
        orders = Order.objects.filter(user=owner)
        serializer = OrderListSerializer(orders, many=True)

        self.assertNotEqual(result.data, serializer.data)

    def test_retrieve_order(self):
        order = Order.objects.get(pk=1)
        url = detail_url(order.id)
        result = self.client.get(url)
        serializer = OrderListSerializer(order)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_order(self):
        owner = get_user_model().objects.get(pk=1)
        flight_1 = Flight.objects.get(pk=1)
        new_order = Order.objects.create(created_at="2023-05-24 13:50", user=owner)
        ticket_data = {
            "row": 11,
            "seat": 4,
            "flight": flight_1.id,
            "order": new_order.id,
        }

        result = self.client.post(
            ORDER_URL,
            {
                "tickets": [ticket_data],
                "created_at": "2023-05-24 13:50",
                "user": owner.id,
            },
            format="json",
        )

        order = Order.objects.get(id=result.data["id"])
        ticket = Ticket.objects.get(id=result.data["tickets"][0]["id"])
        serializer_order = OrderSerializer(order)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.data, serializer_order.data)
        self.assertEqual(ticket_data["row"], ticket.row)
        self.assertEqual(ticket_data["seat"], ticket.seat)
        self.assertEqual(order.tickets.all()[0], ticket)

    def test_update_order_not_allowed(self):
        order = Order.objects.get(pk=1)
        url = detail_url(order.id)
        result = self.client.put(url)

        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_order_not_allowed(self):
        order = Order.objects.get(pk=1)
        url = detail_url(order.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
