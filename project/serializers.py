from rest_framework import serializers
from .models import (
    Project, TransportType, Stop, Route, RouteStop, Connection,
    Vehicle, VehiclePosition
)

class TransportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportType
        fields = ['id', 'name']


class StopSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    class Meta:
        model = Stop
        fields = ['id', 'name', 'location', 'latitude', 'longitude']


class RouteSerializer(serializers.ModelSerializer):
    transport_type = serializers.PrimaryKeyRelatedField(queryset=TransportType.objects.all())
    class Meta:
        model = Route
        fields = ['id', 'name', 'transport_type']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['transport_type'] = TransportTypeSerializer(instance.transport_type).data
        except TransportType.DoesNotExist:
            representation['transport_type'] = None
        return representation


class RouteStopSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    stop = serializers.PrimaryKeyRelatedField(queryset=Stop.objects.all())
    class Meta:
        model = RouteStop
        fields = ['id', 'route', 'stop', 'order']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['route'] = RouteSerializer(instance.route).data
        except Route.DoesNotExist:
            representation['route'] = None
        try:
            representation['stop'] = StopSerializer(instance.stop).data
        except Stop.DoesNotExist:
            representation['stop'] = None
        return representation


class ConnectionSerializer(serializers.ModelSerializer):
    from_stop = serializers.PrimaryKeyRelatedField(queryset=Stop.objects.all())
    to_stop = serializers.PrimaryKeyRelatedField(queryset=Stop.objects.all())
    class Meta:
        model = Connection
        fields = ['id', 'from_stop', 'to_stop', 'travel_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['from_stop'] = StopSerializer(instance.from_stop).data
        except Stop.DoesNotExist:
            representation['from_stop'] = None
        try:
            representation['to_stop'] = StopSerializer(instance.to_stop).data
        except Stop.DoesNotExist:
            representation['to_stop'] = None
        return representation


class ProjectSerializer(serializers.ModelSerializer):
    transport_types = serializers.PrimaryKeyRelatedField(many=True, queryset=TransportType.objects.all())
    stops = serializers.PrimaryKeyRelatedField(many=True, queryset=Stop.objects.all())
    routes = serializers.PrimaryKeyRelatedField(many=True, queryset=Route.objects.all())
    route_stops = serializers.PrimaryKeyRelatedField(many=True, queryset=RouteStop.objects.all())
    connections = serializers.PrimaryKeyRelatedField(many=True, queryset=Connection.objects.all())
    class Meta:
        model = Project
        fields = ['id', 'name', 'transport_types', 'stops', 'routes', 'route_stops', 'connections']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['transport_types'] = TransportTypeSerializer(instance.transport_types.all(), many=True).data
        representation['stops'] = StopSerializer(instance.stops.all(), many=True).data
        representation['routes'] = RouteSerializer(instance.routes.all(), many=True).data
        representation['route_stops'] = RouteStopSerializer(instance.route_stops.all(), many=True).data
        representation['connections'] = ConnectionSerializer(instance.connections.all(), many=True).data
        return representation

class VehicleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели транспортного средства."""
    class Meta:
        model = Vehicle
        fields = ['id', 'gos_num']


class VehiclePositionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели позиций ТС."""
    # Добавляем read-only поля для удобства фронтенда
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)    
    vehicle = VehicleSerializer(read_only=True)
    route = RouteSerializer(read_only=True)

    class Meta:
        model = VehiclePosition
        fields = [
            'id', 'timestamp', 'location', 'latitude', 'longitude', 
            'speed', 'direction', 'vehicle', 'route'
        ]