from django.contrib import admin
from .models import TransportType, Stop, Route, RouteStop, Connection

@admin.register(TransportType)
class TransportTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'transport_type')
    list_filter = ('transport_type',)
    search_fields = ('name',)

@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'stop', 'order')
    list_filter = ('route',)
    search_fields = ('route__name', 'stop__name')

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_stop', 'to_stop', 'travel_time')
    list_filter = ('from_stop', 'to_stop')
    search_fields = ('from_stop__name', 'to_stop__name')
