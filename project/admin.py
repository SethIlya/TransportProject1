# project/admin.py

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin # <-- ИСПРАВЛЕНИЕ: Прямой импорт OSMGeoAdmin
from .models import (
    Project, TransportType, Stop, Route, RouteStop, Connection, Vehicle, VehiclePosition
)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('transport_types', 'stops', 'routes', 'route_stops', 'connections')

@admin.register(TransportType)
class TransportTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# <-- ИСПРАВЛЕНИЕ: Класс наследуется от OSMGeoAdmin, а не от ModelAdmin
@admin.register(Stop)
class StopAdmin(OSMGeoAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude')
    search_fields = ('name',)
    # OSMGeoAdmin автоматически подхватит поле 'location' для карты
    default_lat = 52.28  # Центр карты по умолчанию (Иркутск)
    default_lon = 104.30 # Центр карты по умолчанию (Иркутск)
    default_zoom = 11

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
    autocomplete_fields = ['route', 'stop'] # Улучшает выбор в админке

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_stop', 'to_stop', 'travel_time')
    list_filter = ('from_stop', 'to_stop')
    search_fields = ('from_stop__name', 'to_stop__name')
    autocomplete_fields = ['from_stop', 'to_stop']

# --- Регистрация новых моделей ---

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'gos_num')
    search_fields = ('gos_num',)

# <-- ИСПРАВЛЕНИЕ: Класс наследуется от OSMGeoAdmin
@admin.register(VehiclePosition)
class VehiclePositionAdmin(OSMGeoAdmin):
    list_display = ('id', 'vehicle', 'route', 'timestamp', 'speed')
    list_filter = ('route', 'timestamp')
    search_fields = ('vehicle__gos_num',)
    list_per_page = 25
    # OSMGeoAdmin автоматически подхватит поле 'location' для карты
    default_lat = 52.28
    default_lon = 104.30
    default_zoom = 11