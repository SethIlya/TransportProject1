from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    TransportType, Stop, Route, RouteStop, 
    Connection, Vehicle, VehiclePosition, Project
)

class TransportModelTest(TestCase):
    def setUp(self):
        self.ttype = TransportType.objects.create(name="Автобус")
        self.stop1 = Stop.objects.create(name="Остановка А", location=Point(104.28, 52.28, srid=4326))
        self.stop2 = Stop.objects.create(name="Остановка Б", location=Point(104.30, 52.30, srid=4326))
        self.route = Route.objects.create(name="Маршрут 1", transport_type=self.ttype)

    def test_transport_type_creation(self):
        self.assertEqual(self.ttype.name, "Автобус")
        self.assertEqual(str(self.ttype), "Автобус")

    def test_stop_properties(self):
        self.assertEqual(self.stop1.latitude, 52.28)
        self.assertEqual(self.stop1.longitude, 104.28)
        self.assertTrue("Остановка А" in str(self.stop1))

    def test_route_stop_creation(self):
        rs = RouteStop.objects.create(route=self.route, stop=self.stop1, order=1)
        self.assertEqual(rs.order, 1)
        self.assertEqual(rs.route, self.route)

    def test_vehicle_position(self):
        veh = Vehicle.objects.create(gos_num="А123АА38")
        pos = VehiclePosition.objects.create(
            vehicle=veh,
            route=self.route,
            timestamp=timezone.now(),
            location=Point(104.29, 52.29, srid=4326),
            speed=40
        )
        self.assertEqual(pos.speed, 40)
        self.assertEqual(pos.vehicle.gos_num, "А123АА38")


class ApiEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ttype = TransportType.objects.create(name="Трамвай")
        self.stop_in = Stop.objects.create(name="Центр", location=Point(104.28, 52.28, srid=4326))
        self.stop_out = Stop.objects.create(name="Пригород", location=Point(105.00, 53.00, srid=4326))
        
        # WKT полигон, покрывающий "Центр" (104.0, 52.0 -> 104.5, 52.5), но исключающий "Пригород"
        self.poly_wkt = Polygon((
            (104.0, 52.0), 
            (104.5, 52.0), 
            (104.5, 52.5), 
            (104.0, 52.5), 
            (104.0, 52.0)
        ), srid=4326).wkt

    def test_get_stops_list(self):
        response = self.client.get('/api/stops/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_stop(self):
        data = {
            "name": "Новая остановка",
            "location": "POINT(104.31 52.31)"
        }
        response = self.client.post('/api/stops/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stop.objects.count(), 3)

    def test_spatial_filter_polygon_stops(self):
        """Тест фильтрации геоданных по полигону."""
        response = self.client.get(f'/api/stops/?polygon={self.poly_wkt}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Внутри полигона только 1 остановка ("Центр")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Центр")

    def test_spatial_filter_polygon_vehicles(self):
        veh = Vehicle.objects.create(gos_num="Т001ТТ38")
        # Транспорт внутри полигона
        VehiclePosition.objects.create(
            vehicle=veh, timestamp=timezone.now(),
            location=Point(104.28, 52.28, srid=4326)
        )
        # Транспорт вне полигона
        VehiclePosition.objects.create(
            vehicle=veh, timestamp=timezone.now() - timezone.timedelta(minutes=10),
            location=Point(105.00, 53.00, srid=4326)
        )

        response = self.client.get(f'/api/vehicle-positions/?polygon={self.poly_wkt}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertAlmostEqual(response.data[0]['latitude'], 52.28)

class FullCrudApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Начальные данные для тестов
        self.t_type = TransportType.objects.create(name="Автобус")
        self.stop = Stop.objects.create(
            name="Тестовая остановка", 
            location=Point(104.0, 52.0, srid=4326)
        )
        self.route = Route.objects.create(name="100", transport_type=self.t_type)

    def test_crud_transport_type(self):
        # 1. Создание
        data = {"name": "Троллейбус"}
        response = self.client.post('/api/transport-types/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_id = response.data['id']

        # 2. Чтение конкретного объекта
        response = self.client.get(f('/api/transport-types/{new_id}/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Троллейбус")

        # 3. Обновление через PATCH
        response = self.client.patch(f('/api/transport-types/{new_id}/'), {"name": "Электробус"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TransportType.objects.get(id=new_id).name, "Электробус")

        # 4. Удаление
        response = self.client.delete(f('/api/transport-types/{new_id}/'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TransportType.objects.filter(id=new_id).exists())

    def test_update_stop_location(self):
        """Тест изменения координат остановки."""
        update_data = {
            "name": "Переименованная остановка",
            "location": "POINT(104.5 52.5)"
        }
        response = self.client.put(f('/api/stops/{self.stop.id}/'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что в БД данные обновились
        self.stop.refresh_from_db()
        self.assertEqual(self.stop.name, "Переименованная остановка")
        self.assertEqual(self.stop.location.x, 104.5)

    # ТЕСТЫ МАРШРУТОВ 
    def test_route_detail_and_list(self):
        """Тест получения списка и деталей маршрута."""
        # Список
        response = self.client.get('/api/routes/')
        self.assertEqual(len(response.data), 1)
        
        # Детали
        response = self.client.get(f('/api/routes/{self.route.id}/'))
        self.assertEqual(response.data['name'], "100")
        # Проверяем, что в ответе есть вложенный тип транспорта (если сериализатор это поддерживает)
        if 'transport_type' in response.data:
            self.assertEqual(response.data['transport_type']['name'], "Автобус")

    # --- ТЕСТЫ ОШИБОК 
    def test_delete_non_existent(self):
        """Попытка удалить несуществующий объект."""
        response = self.client.delete('/api/stops/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_invalid_stop(self):
        """Попытка создать остановку без обязательных полей."""
        response = self.client.post('/api/stops/', {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
