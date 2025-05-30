"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
# from project import views # Оставляем, если ShowProjectView еще нужна
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from project.api import (
    ProjectViewSet, TransportTypeViewSet, StopViewSet,
    RouteViewSet, RouteStopViewSet, ConnectionViewSet,
    FileUploadView # <-- Импортируем новое представление загрузки
)

# Убедитесь, что ShowProjectView все еще импортируется, если используется в urlpatterns
from project.views import ShowProjectView # <-- Явно импортируем, если она нужна


router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'transport-types', TransportTypeViewSet, basename='transport-types')
router.register(r'stops', StopViewSet, basename='stops')
router.register(r'routes', RouteViewSet, basename='routes')
router.register(r'route-stops', RouteStopViewSet, basename='route-stops')
router.register(r'connections', ConnectionViewSet, basename='connections')

urlpatterns = [

    path('', ShowProjectView.as_view(), name='show_project'), 

    path('api/', include(router.urls)),

    path('api/upload-geojson/', FileUploadView.as_view(), name='upload_geojson'), 

    path('admin/', admin.site.urls),
]

