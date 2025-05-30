# project/api.py

# project/api.py

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
import json
# Импортируем класс Point из GeoDjango для создания географических объектов
from django.contrib.gis.geos import Point
import traceback

from project.models import (
    Project, TransportType, Stop, Route, RouteStop, Connection
)
# Импортируем все сериализаторы (обновленные в serializers.py)
from project.serializers import (
    ProjectSerializer, TransportTypeSerializer, StopSerializer,
    RouteSerializer, RouteStopSerializer, ConnectionSerializer
)

# --- Standard CRUD ViewSets (using updated serializers) ---
# Эти ViewSet'ы используют обновленные сериализаторы, которые теперь корректно
# обрабатывают ForeignKeys/ManyToManys для записи и чтения.

class ProjectViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TransportTypeViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = TransportType.objects.all()
    serializer_class = TransportTypeSerializer


class StopViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    # Теперь StopSerializer обрабатывает PointField 'location'
    # Фронтенд должен отправлять данные для 'location' (например, WKT или GeoJSON Point)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    # RouteSerializer теперь корректно обрабатывает ForeignKey 'transport_type'


class RouteStopViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer
    # RouteStopSerializer теперь корректно обрабатывает ForeignKeys 'route' и 'stop'


class ConnectionViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    # ConnectionSerializer теперь корректно обрабатывает ForeignKeys 'from_stop' и 'to_stop'

# --- File Upload View (updated to handle PointField) ---

class FileUploadView(APIView):
    """
    Принимает файл GeoJSON, парсит его и создает/обновляет объекты Stop.
    Теперь сохраняет координаты в поле 'location' типа PointField.
    """
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('geojson_file')
        if not file_obj:
            return Response(
                {"error": "Файл GeoJSON не предоставлен."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.name.lower().endswith('.geojson'):
             return Response(
                {"error": "Файл должен быть в формате GeoJSON (.geojson)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_content = file_obj.read().decode('utf-8')
            geojson_data = json.loads(file_content)

            if geojson_data.get("type") != "FeatureCollection" or "features" not in geojson_data:
                 return Response(
                    {"error": "Некорректный формат GeoJSON. Ожидается FeatureCollection с массивом features."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            features = geojson_data.get("features", [])
            stops_created_count = 0
            stops_updated_count = 0
            errors = []

            for i, feature in enumerate(features):
                try:
                    if feature.get("type") != "Feature":
                        errors.append(f"Запись #{i+1}: Пропущена некорректная запись (не 'Feature'): {feature}")
                        continue

                    properties = feature.get("properties", {})
                    geometry = feature.get("geometry", {})

                    stop_name = properties.get("NAME")
                    coords = geometry.get("coordinates") # GeoJSON: [longitude, latitude]
                    geom_type = geometry.get("type") # Тип геометрии (например, "Point")


                    # Проверка минимально необходимых данных и типа геометрии
                    if not stop_name or not coords or not isinstance(coords, list) or len(coords) < 2 or geom_type != "Point":
                         errors.append(f"Запись #{i+1}: Пропущена или имеет некорректные данные (отсутствует NAME, координаты, или тип геометрии не Point): {feature}")
                         continue

                    longitude = coords[0]
                    latitude = coords[1]

                     # Проверяем тип координат
                    if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
                         errors.append(f"Запись #{i+1}: Некорректный формат координат (ожидаются числа): {feature}")
                         continue


                    # СОЗДАЕМ ОБЪЕКТ POINT для GeoDjango PointField
                    # Point ожидает Point(долгота, широта)
                    location_point = Point(longitude, latitude, srid=4326) # Используем srid 4326


                    # Попробуем найти остановку по имени для обновления, иначе создаем новую
                    # Если вы добавили уникальное поле из GeoJSON (например, 'id') в модель Stop,
                    # лучше использовать его для update_or_create:
                    # geojson_id = properties.get("id")
                    # if geojson_id is not None:
                    #    stop, created = Stop.objects.update_or_create(
                    #        geojson_id=geojson_id, # Предполагая, что добавили поле geojson_id в модель Stop
                    #        defaults={
                    #            'name': stop_name,
                    #            'location': location_point
                    #        }
                    #    )
                    # else: # Fallback к имени или пропустить
                    #     errors.append(f"Запись #{i+1}: Отсутствует уникальный ID (id) для обновления/создания: {feature}")
                    #     continue

                    # Текущая логика update_or_create по имени:
                    stop, created = Stop.objects.update_or_create(
                        name=stop_name,
                        defaults={
                            'location': location_point # <-- Сохраняем объект Point
                            # Поля latitude/longitude из старой модели удалены
                        }
                    )

                    if created:
                        stops_created_count += 1
                    else:
                        stops_updated_count += 1

                except Exception as e:
                    errors.append(f"Запись #{i+1} (NAME: {properties.get('NAME', 'N/A')}): Ошибка обработки - {e} - Трейсбэк: {traceback.format_exc()}")

                # TODO: Добавьте здесь логику для импорта других моделей (Route, Connection и т.д.)
                # если данные для них присутствуют в других Feature или другом формате в файле.
                # Например, если есть Feature с геометрией LineString, это может быть маршрут.
                # Это потребует анализа структуры вашего конкретного файла GeoJSON для маршрутов.


            # Возвращаем ответ с количеством созданных/обновленных объектов и списком ошибок
            return Response(
                {
                    "message": "Импорт успешно завершен.",
                    "stops_created": stops_created_count,
                    "stops_updated": stops_updated_count,
                    "errors": errors
                },
                status=status.HTTP_200_OK
            )

        except json.JSONDecodeError:
             return Response(
                {"error": "Некорректный формат JSON в файле."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Общая ошибка при обработке файла (не парсинг, а чтение или другая проблема)
            return Response(
                {"error": f"Ошибка при обработке файла: {e}", "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )