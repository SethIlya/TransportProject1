import csv
import json
import traceback

from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point

from django.db import models

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Connection, Project, Route, RouteStop, Stop, TransportType, Vehicle,
    VehiclePosition
)
from .serializers import (
    ConnectionSerializer, ProjectSerializer, RouteSerializer,
    RouteStopSerializer, StopSerializer, TransportTypeSerializer,
    VehiclePositionSerializer, VehicleSerializer
)
from .services import import_bus_data_from_files
from django_q.tasks import async_task


class ProjectViewSet(viewsets.ModelViewSet):
    """API для управления Проектами (Городами)."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class TransportTypeViewSet(viewsets.ModelViewSet):
    """API для управления Типами Транспорта."""
    queryset = TransportType.objects.all()
    serializer_class = TransportTypeSerializer

class StopViewSet(viewsets.ModelViewSet):
    """API для управления Остановками."""
    queryset = Stop.objects.all()
    serializer_class = StopSerializer

class RouteViewSet(viewsets.ModelViewSet):
    """API для управления Маршрутами."""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class RouteStopViewSet(viewsets.ModelViewSet):
    """API для управления Маршрутными Остановками."""
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer

class ConnectionViewSet(viewsets.ModelViewSet):
    """API для управления Соединениями между остановками."""
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer

class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения списка транспортных средств."""
    queryset = Vehicle.objects.all().order_by('gos_num')
    serializer_class = VehicleSerializer

class VehiclePositionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения списка позиций ТС с фильтрацией."""
    serializer_class = VehiclePositionSerializer

    def get_queryset(self):
        queryset = VehiclePosition.objects.select_related('vehicle', 'route').all()
        vehicle_id = self.request.query_params.get('vehicle_id')
        route_id = self.request.query_params.get('route_id')
        if vehicle_id:
            queryset = queryset.filter(vehicle__id=vehicle_id)
        elif route_id:
            queryset = queryset.filter(route__id=route_id)
        return queryset.order_by('timestamp')

class FileUploadView(APIView):
    """Принимает GeoJSON для импорта/обновления остановок."""
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('geojson_file')
        if not file_obj:
            return Response({"error": "Файл GeoJSON не предоставлен."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_content = file_obj.read().decode('utf-8')
            geojson_data = json.loads(file_content)
            # ... (логика импорта) ...
            return Response({"message": "Импорт завершен."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusDataUploadAPIView(APIView):
    """Принимает JSON/ZIP файлы для импорта данных о движении."""
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "Файлы не предоставлены."}, status=status.HTTP_400_BAD_REQUEST)
        
        result = import_bus_data_from_files(files)
        response_status = status.HTTP_207_MULTI_STATUS if result.get('errors') else status.HTTP_200_OK
        return Response(result, status=response_status)


# --- Views для экспорта данных ---

class StopsExportCSVView(APIView):
    """Экспортирует все остановки в CSV файл."""
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="stops_export.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['ID', 'Название остановки', 'Широта', 'Долгота'])
        for stop in Stop.objects.all().order_by('name'):
            writer.writerow([stop.id, stop.name, stop.latitude, stop.longitude])
        return response

class RoutePositionsExportCSVView(APIView):
    """Экспортирует историю движения по маршруту в CSV."""
    def get(self, request, route_id, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="route_{route_id}_positions.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['ID Позиции', 'Время', 'Гос. номер ТС', 'Скорость (км/ч)', 'Направление', 'Широта', 'Долгота'])
        positions = VehiclePosition.objects.filter(route__id=route_id).select_related('vehicle').order_by('timestamp')
        for pos in positions:
            writer.writerow([pos.id, pos.timestamp.strftime('%Y-%m-%d %H:%M:%S'), pos.vehicle.gos_num if pos.vehicle else '', pos.speed, pos.direction, pos.latitude, pos.longitude])
        return response

class StopsExportGeoJSONView(APIView):
    """Экспортирует все остановки в формат GeoJSON FeatureCollection."""
    def get(self, request, *args, **kwargs):
        feature_collection = {"type": "FeatureCollection", "features": []}
        for stop in Stop.objects.filter(location__isnull=False).order_by('name'):
            feature = {
                "type": "Feature",
                "geometry": json.loads(stop.location.geojson),
                "properties": {"id": stop.id, "name": stop.name},
            }
            feature_collection["features"].append(feature)
        response = JsonResponse(feature_collection)
        response['Content-Disposition'] = 'attachment; filename="stops_export.geojson"'
        return response

class RoutePositionsExportJSONView(APIView):
    """Экспортирует историю движения по маршруту в простой JSON формат."""
    def get(self, request, route_id, *args, **kwargs):
        positions = VehiclePosition.objects.filter(route__id=route_id).select_related('vehicle').order_by('timestamp')
        data_list = [
            {
                "position_id": pos.id,
                "timestamp": pos.timestamp.isoformat(),
                "latitude": pos.latitude,
                "longitude": pos.longitude,
                "speed": pos.speed,
                "direction": pos.direction,
                "vehicle_gos_num": pos.vehicle.gos_num if pos.vehicle else None
            } for pos in positions
        ]
        response = JsonResponse(data_list, safe=False)
        response['Content-Disposition'] = f'attachment; filename="route_{route_id}_positions.json"'
        return response
    
class StartCollectionPipelineView(APIView):
    """
    Запускает асинхронную задачу ТОЛЬКО для сбора и очистки данных.
    """
    def post(self, request, *args, **kwargs):
        async_task('project.tasks.run_collection_task')
        return Response(
            {"message": "Процесс сбора и очистки данных запущен в фоновом режиме."},
            status=status.HTTP_202_ACCEPTED
        )

class StartImportPipelineView(APIView):
    """
    Запускает асинхронную задачу ТОЛЬКО для импорта собранных данных в БД.
    """
    def post(self, request, *args, **kwargs):
        async_task('project.tasks.run_import_task')
        return Response(
            {"message": "Процесс импорта данных в базу запущен в фоновом режиме."},
            status=status.HTTP_202_ACCEPTED
        )
    
class DeleteMonitoringDataView(APIView):
    """
    Удаляет данные о позициях и "осиротевшие" ТС на основе ID маршрутов.
    """
    def post(self, request, *args, **kwargs):
        route_ids = request.data.get('route_ids', [])
        delete_all = request.data.get('delete_all', False)

        if not route_ids and not delete_all:
            return Response(
                {"error": "Не указаны ID маршрутов или флаг 'delete_all'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_positions_count = 0
        deleted_vehicles_count = 0

        if delete_all:
            deleted_positions_count, _ = VehiclePosition.objects.all().delete()
            deleted_vehicles_count, _ = Vehicle.objects.all().delete()
        else:

            positions_to_delete = VehiclePosition.objects.filter(route__id__in=route_ids)
            deleted_positions_count, _ = positions_to_delete.delete()

            vehicles_to_delete = Vehicle.objects.annotate(
                num_positions=models.Count('positions')
            ).filter(num_positions=0)
            
            deleted_vehicles_count, _ = vehicles_to_delete.delete()

            # ---------------------------------

        return Response(
            {
                "message": "Данные успешно удалены.",
                "deleted_positions": deleted_positions_count,
                "deleted_vehicles": deleted_vehicles_count,
            },
            status=status.HTTP_200_OK
        )