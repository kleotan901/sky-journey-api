from django.contrib import admin

from airport.models import (
    Crew,
    Route,
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Flight,
    Ticket,
    Order,
)


admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Order)
