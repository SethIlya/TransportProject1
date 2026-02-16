# project/models.py

from django.db import models
from django.contrib.gis.db import models as gis_models

class TransportType(models.Model):
    name = models.CharField("Название типа транспорта", max_length=100, unique=True)
    class Meta:
        verbose_name = "Тип транспорта"
        verbose_name_plural = "Типы транспорта"
    def __str__(self):
        return self.name

class Stop(models.Model):
    name = models.CharField("Название остановки", max_length=200)
    # Используем PointField для хранения географических координат
    location = gis_models.PointField("Географическое положение", srid=4326, blank=True, null=True)
    class Meta:
        verbose_name = "Остановка"
        verbose_name_plural = "Остановки"

    def __str__(self):
        coords_str = f"({self.latitude:.6f}, {self.longitude:.6f})" if self.location else "N/A"
        return f"{self.name} {coords_str}"

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

class Route(models.Model):
    name = models.CharField("Название маршрута", max_length=200)
    transport_type = models.ForeignKey(
        TransportType,
        verbose_name="Тип транспорта",
        on_delete=models.PROTECT
    )
    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
    def __str__(self):
        return self.name

class RouteStop(models.Model):
    route = models.ForeignKey(Route, verbose_name="Маршрут", on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, verbose_name="Остановка", on_delete=models.CASCADE)
    order = models.PositiveIntegerField("Порядковый номер на маршруте")
    class Meta:
        verbose_name = "Маршрутная остановка"
        verbose_name_plural = "Маршрутные остановки"
        ordering = ['route', 'order']
        unique_together = ('route', 'order')
    def __str__(self):
        route_name = self.route.name if self.route else "Неизвестный маршрут"
        stop_name = self.stop.name if self.stop else "Неизвестная остановка"
        return f"{route_name} - {stop_name} (#{self.order})"

class Connection(models.Model):
    from_stop = models.ForeignKey(Stop, verbose_name="Остановка отправления", on_delete=models.CASCADE, related_name='from_connections')
    to_stop = models.ForeignKey(Stop, verbose_name="Остановка прибытия", on_delete=models.CASCADE, related_name='to_connections')
    travel_time = models.IntegerField("Время в пути (мин)")
    class Meta:
        verbose_name = "Соединение"
        verbose_name_plural = "Соединения"
        unique_together = ('from_stop', 'to_stop')
    def __str__(self):
        from_name = self.from_stop.name if self.from_stop else "Неизвестная остановка"
        to_name = self.to_stop.name if self.to_stop else "Неизвестная остановка"
        return f"{from_name} -> {to_name} ({self.travel_time} мин)"

class Project(models.Model):
    name = models.CharField("Название проекта", max_length=200, unique=True)
    transport_types = models.ManyToManyField(TransportType, verbose_name="Типы транспорта", blank=True)
    stops = models.ManyToManyField(Stop, verbose_name="Остановки", blank=True)
    routes = models.ManyToManyField(Route, verbose_name="Маршруты", blank=True)
    route_stops = models.ManyToManyField(RouteStop, verbose_name="Маршрутные остановки", blank=True)
    connections = models.ManyToManyField(Connection, verbose_name="Соединения", blank=True)
    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
    def __str__(self):
        return self.name

class Vehicle(models.Model):
    """Модель для транспортного средства (автобуса)."""
    gos_num = models.CharField("Гос. номер", max_length=20, unique=True, db_index=True)
    class Meta:
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"
    def __str__(self):
        return self.gos_num

class VehiclePosition(models.Model):
    """Модель для хранения одной точки местоположения ТС в определенное время."""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="positions", verbose_name="Транспорт")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Маршрут")
    timestamp = models.DateTimeField("Время", db_index=True)
    location = gis_models.PointField("Местоположение", srid=4326) # SRID 4326 для WGS 84
    speed = models.PositiveIntegerField("Скорость", default=0)
    direction = models.PositiveIntegerField("Направление (азимут)", default=0)

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

    class Meta:
        verbose_name = "Позиция ТС"
        verbose_name_plural = "Позиции ТС"
        ordering = ['-timestamp']
        unique_together = ('vehicle', 'timestamp') # Предотвращаем дублирование позиций одного ТС в одно время

    def __str__(self):
        return f"{self.vehicle.gos_num} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"