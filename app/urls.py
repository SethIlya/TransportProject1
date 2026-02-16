from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project.views import ShowProjectView
from project.api import (
    ProjectViewSet, TransportTypeViewSet, StopViewSet,
    RouteViewSet, RouteStopViewSet, ConnectionViewSet,
    FileUploadView, BusDataUploadAPIView,
    VehicleViewSet, VehiclePositionViewSet,
    StopsExportCSVView, RoutePositionsExportCSVView,
    StopsExportGeoJSONView,
    RoutePositionsExportJSONView,
    StartCollectionPipelineView, StartImportPipelineView, DeleteMonitoringDataView    # <-- Импортируем правильный View
)

# Создаем роутер
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'transport-types', TransportTypeViewSet, basename='transport-types')
router.register(r'stops', StopViewSet, basename='stops')
router.register(r'routes', RouteViewSet, basename='routes')
router.register(r'route-stops', RouteStopViewSet, basename='route-stops')
router.register(r'connections', ConnectionViewSet, basename='connections')
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'vehicle-positions', VehiclePositionViewSet, basename='vehicle-positions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ShowProjectView.as_view(), name='show_project'),
    path('api/', include(router.urls)),
    
    # URL для импорта
    path('api/upload-geojson/', FileUploadView.as_view(), name='upload_geojson'),
    path('api/upload-bus-data/', BusDataUploadAPIView.as_view(), name='upload_bus_data'),

    # URL для экспорта остановок
    path('api/export/stops/csv/', StopsExportCSVView.as_view(), name='export-stops-csv'),
    path('api/export/stops/geojson/', StopsExportGeoJSONView.as_view(), name='export-stops-geojson'),

    # URL для экспорта позиций по маршруту
    path('api/export/route-positions/<int:route_id>/csv/', RoutePositionsExportCSVView.as_view(), name='export-route-positions-csv'),
    path('api/export/route-positions/<int:route_id>/json/', RoutePositionsExportJSONView.as_view(), name='export-route-positions-json'),

    path('api/start-collection-pipeline/', StartCollectionPipelineView.as_view(), name='start_collection_pipeline'),
    path('api/start-import-pipeline/', StartImportPipelineView.as_view(), name='start_import_pipeline'),
    
    path('api/delete-monitoring-data/', DeleteMonitoringDataView.as_view(), name='delete_monitoring_data'),
]