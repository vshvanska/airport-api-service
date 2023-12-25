from django.contrib import admin

from flights.models import (
    Airport,
    Crew,
    AirplaneType,
    Order,
    Route,
    Airplane,
    Flight,
    Ticket,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    list_filter = ("closest_big_city",)
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user")
    list_filter = ("user",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source", "destination")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type")
    list_filter = ("airplane_type",)
    search_fields = ("name",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("route", "airplane", "departure_time", "arrival_time")
    list_filter = ("departure_time",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("flight", "row", "seat", "order")
    list_filter = ("flight", "order")


admin.site.register(Crew)
admin.site.register(AirplaneType)
