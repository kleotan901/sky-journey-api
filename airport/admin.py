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


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Flight)
