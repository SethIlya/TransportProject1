# project/models.py
# project/models.py

from django.db import models
# Импортируем модели из GeoDjango для географических полей
from django.contrib.gis.db import models as gis_models

class TransportType(models.Model):
    name = models.CharField("Название типа транспорта", max_length=100, unique=True)

    class Meta:
        verbose_name = "Тип транспорта"
        verbose_name_plural = "Типы транспорта"

    def __str__(self) -> str:
        return self.name


class Stop(models.Model):
    name = models.CharField("Название остановки", max_length=200)
    # Удалены старые поля широты и долготы (если они были)
    # latitude = models.FloatField("Широта")
    # longitude = models.FloatField("Долгота")

    # Добавляем поле PointField для хранения координат
    # srid=4326 - это стандартная система координат WGS 84
    location = gis_models.PointField("Географическое положение", srid=4326, blank=True, null=True)

    class Meta:
        verbose_name = "Остановка"
        verbose_name_plural = "Остановки"
        # Можно добавить уникальность пары имя-местоположение, если требуется
        # unique_together = ('name', 'location')

    def __str__(self) -> str:
        # Добавляем координаты в строковое представление для удобства
        coords_str = f"({self.latitude:.6f}, {self.longitude:.6f})" if self.location else "N/A"
        return f"{self.name} {coords_str}"

    # Свойства для удобного доступа к широте и долготе из PointField
    @property
    def latitude(self):
        return self.location.y if self.location else None # В GeoDjango Point (x=долгота, y=широта)

    @property
    def longitude(self):
        return self.location.x if self.location else None


class Route(models.Model):
    name = models.CharField("Название маршрута", max_length=200)
    transport_type = models.ForeignKey(
        TransportType,
        verbose_name="Тип транспорта",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self) -> str:
        return self.name


class RouteStop(models.Model):
    route = models.ForeignKey(
        Route,
        verbose_name="Маршрут",
        on_delete=models.CASCADE
    )
    stop = models.ForeignKey(
        Stop,
        verbose_name="Остановка",
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField("Порядковый номер на маршруте")

    class Meta:
        verbose_name = "Маршрутная остановка"
        verbose_name_plural = "Маршрутные остановки"
        ordering = ['route', 'order']
        # Добавляем уникальность пары маршрут-остановка-порядок
        unique_together = ('route', 'order') # Или ('route', 'stop'), в зависимости от логики

    def __str__(self) -> str:
        # Используем безопасный доступ к связанным объектам на случай, если один из них был удален
        route_name = self.route.name if self.route else "Неизвестный маршрут"
        stop_name = self.stop.name if self.stop else "Неизвестная остановка"
        return f"{route_name} - {stop_name} (#{self.order})"


class Connection(models.Model):
    from_stop = models.ForeignKey(
        Stop,
        verbose_name="Остановка отправления",
        on_delete=models.CASCADE,
        related_name='from_connections'
    )
    to_stop = models.ForeignKey(
        Stop,
        verbose_name="Остановка прибытия",
        on_delete=models.CASCADE,
        related_name='to_connections'
    )
    travel_time = models.IntegerField("Время в пути (мин)")

    class Meta:
        verbose_name = "Соединение"
        verbose_name_plural = "Соединения"
        # Добавляем уникальность пары остановок (в одном направлении)
        unique_together = ('from_stop', 'to_stop')


    def __str__(self) -> str:
        from_name = self.from_stop.name if self.from_stop else "Неизвестная остановка"
        to_name = self.to_stop.name if self.to_stop else "Неизвестная остановка"
        return f"{from_name} -> {to_name} ({self.travel_time} мин)"


# Модель Project, объединяющая остальные (ссылается на обновленную модель Stop)
class Project(models.Model):
    name = models.CharField("Название проекта", max_length=200, unique=True)
    transport_types = models.ManyToManyField(TransportType, verbose_name="Типы транспорта", blank=True)
    # ManyToMany к Stop (которая теперь с PointField)
    stops = models.ManyToManyField(Stop, verbose_name="Остановки", blank=True)
    routes = models.ManyToManyField(Route, verbose_name="Маршруты", blank=True)
    route_stops = models.ManyToManyField(RouteStop, verbose_name="Маршрутные остановки", blank=True)
    connections = models.ManyToManyField(Connection, verbose_name="Соединения", blank=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self) -> str:
        return self.name