from django.urls import path, include
from rest_framework import routers

from airport.views import (
    CrewViewSet,
    CityViewSet,
    CountryViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airplane", AirplaneViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
