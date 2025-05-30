# project/serializers.py

from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer # Можно использовать для более сложной работы с GeoJSON форматом

# Импортируем модели
from project.models import (
    Project, TransportType, Stop, Route, RouteStop, Connection
)

# --- Сериализаторы для стандартного CRUD API ---
# Изменены, чтобы Foreign Keys были PrimaryKeyRelatedField для записи,
# и переопределен to_representation для вывода вложенных объектов.

class TransportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportType
        fields = ['id', 'name']


class StopSerializer(serializers.ModelSerializer):
    # Поле location типа PointField обрабатывается ModelSerializer автоматически для ввода/вывода.
    # Оно примет WKT или GeoJSON Point на вход и, по умолчанию, выведет их же (или другой формат в зависимости от рендерера).

    # Добавляем свойства latitude и longitude как read-only поля для удобства вывода,
    # используя соответствующие @property методы в модели Stop.
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Stop
        # Включаем 'location' для записи/чтения (принимает WKT/GeoJSON Point, отдает WKT/GeoJSON Point).
        # Включаем 'latitude' и 'longitude' для чтения (@property).
        # Удалите старые поля latitude/longitude, если они были в полях модели.
        fields = ['id', 'name', 'location', 'latitude', 'longitude']

    # Нет необходимости переопределять create/update или validate_location,
    # если вы планируете отправлять данные для 'location' в формате WKT
    # или стандартном GeoJSON Point, так как ModelSerializer с GeoDjango
    # обычно умеет их обрабатывать автоматически.


class RouteSerializer(serializers.ModelSerializer):
    # transport_type теперь PrimaryKeyRelatedField для записи (принимает ID).
    # Удаляем старое определение с read_only=True.
    transport_type = serializers.PrimaryKeyRelatedField(
        queryset=TransportType.objects.all() # Указываем queryset для валидации входящего ID
    )

    class Meta:
        model = Route
        fields = ['id', 'name', 'transport_type'] # transport_type теперь writable (принимает ID)

    # Переопределяем to_representation для вывода вложенного объекта TransportType при чтении (GET).
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Сериализуем связанный объект TransportType для вывода.
        # Используем try/except на случай, если связанный объект удален, но ссылка осталась.
        try:
            representation['transport_type'] = TransportTypeSerializer(instance.transport_type).data
        except TransportType.DoesNotExist:
             representation['transport_type'] = None # Или другое значение по умолчанию
        return representation


class RouteStopSerializer(serializers.ModelSerializer):
    # route и stop теперь PrimaryKeyRelatedField для записи (принимают ID).
    # Удаляем старые определения с read_only=True.
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    stop = serializers.PrimaryKeyRelatedField(queryset=Stop.objects.all())
    order = serializers.IntegerField() # Соответствует PositiveIntegerField в модели

    class Meta:
        model = RouteStop
        fields = ['id', 'route', 'stop', 'order'] # route и stop теперь writable (принимают ID)
        # Уникальность уникальной пары маршрут-порядок указывается только в модели.
        # Удалите строку unique_together = ('route', 'order') из Meta в сериализаторе, если она была добавлена здесь.


    # Переопределяем to_representation для вывода вложенных объектов Route и Stop при чтении (GET).
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Сериализуем связанные объекты Route и Stop для вывода.
        try:
            # При сериализации Route, его to_representation (если переопределен)
            # будет вызван рекурсивно, сериализуя вложенный transport_type.
            representation['route'] = RouteSerializer(instance.route).data
        except Route.DoesNotExist:
            representation['route'] = None
        try:
            representation['stop'] = StopSerializer(instance.stop).data
        except Stop.DoesNotExist:
            representation['stop'] = None
        return representation


class ConnectionSerializer(serializers.ModelSerializer):
    # from_stop и to_stop теперь PrimaryKeyRelatedField для записи (принимают ID).
    # Удаляем старые определения с read_only=True.
    # related_name используется только в модели, не в сериализаторе. Удалите его здесь.
    from_stop = serializers.PrimaryKeyRelatedField(
        queryset=Stop.objects.all(),
        # related_name='from_connections' # <-- УДАЛИТЕ ЭТУ СТРОКУ
    )
    to_stop = serializers.PrimaryKeyRelatedField(
        queryset=Stop.objects.all(),
        # related_name='to_connections' # <-- УДАЛИТЕ ЭТУ СТРОКУ
    )
    travel_time = serializers.IntegerField() # Соответствует IntegerField в модели

    class Meta:
        model = Connection
        fields = ['id', 'from_stop', 'to_stop', 'travel_time'] # from_stop и to_stop теперь writable (принимают ID)
        # Уникальность уникальной пары from_stop-to_stop указывается только в модели.
        # Удалите строку unique_together = ('from_stop', 'to_stop') из Meta в сериализаторе, если она была добавлена здесь.


    # Переопределяем to_representation для вывода вложенных объектов Stop при чтении (GET).
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Сериализуем связанные объекты Stop для вывода.
        try:
            representation['from_stop'] = StopSerializer(instance.from_stop).data
        except Stop.DoesNotExist:
             representation['from_stop'] = None
        try:
            representation['to_stop'] = StopSerializer(instance.to_stop).data
        except Stop.DoesNotExist:
             representation['to_stop'] = None
        return representation


# --- Измененный ProjectSerializer (Writable ManyToMany) ---
# Этот сериализатор принимает списки ID для ManyToMany полей на запись
# и выводит полные вложенные объекты на чтение (GET).

class ProjectSerializer(serializers.ModelSerializer):
    # Определяем поля ManyToMany как PrimaryKeyRelatedField с many=True для записи (принимают список ID).
    # По умолчанию они также будут выводить список ID при чтении.
    # Удалите старые определения с вложенными сериализаторами и read_only=True.

    transport_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TransportType.objects.all()
    )
    stops = serializers.PrimaryKeyRelatedField( # Ссылается на Stop с PointField
        many=True,
        queryset=Stop.objects.all()
    )
    routes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Route.objects.all()
    )
    route_stops = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=RouteStop.objects.all()
    )
    connections = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Connection.objects.all()
    )

    class Meta:
        model = Project
        # Перечисляем все поля, включая ManyToMany поля, определенные выше.
        # DRF ModelSerializer автоматически свяжет эти поля сериализатора
        # с соответствующими полями модели и будет использовать PrimaryKeyRelatedField(many=True)
        # для их обработки при записи (POST/PUT).
        fields = [
            'id',
            'name',
            'transport_types', # writable (принимает список ID) / readable (выводит список ID по умолчанию)
            'stops',           # writable (принимает список ID) / readable (выводит список ID по умолчанию)
            'routes',          # writable (принимает список ID) / readable (выводит список ID по умолчанию)
            'route_stops',     # writable (принимает список ID) / readable (выводит список ID по умолчанию)
            'connections',     # writable (принимает список ID) / readable (выводит список ID по умолчанию)
        ]

    # Переопределяем метод to_representation для изменения формата ВЫВОДА (GET).
    # Мы хотим выводить полные вложенные объекты вместо списков ID для ManyToMany.
    def to_representation(self, instance):
        # Получаем стандартное представление (будет содержать id, name, и списки ID для ManyToMany от PrimaryKeyRelatedField)
        representation = super().to_representation(instance)

        # Переопределяем ManyToMany поля в представлении, используя вложенные сериализаторы
        # для вывода полных данных связанных объектов.
        representation['transport_types'] = TransportTypeSerializer(instance.transport_types.all(), many=True).data
        # Используем обновленный StopSerializer для Stop объектов (он выведет location и @property lat/lon)
        representation['stops'] = StopSerializer(instance.stops.all(), many=True).data
        # Используем обновленный RouteSerializer и т.д. (их to_representation будет рекурсивно вызваны)
        representation['routes'] = RouteSerializer(instance.routes.all(), many=True).data
        representation['route_stops'] = RouteStopSerializer(instance.route_stops.all(), many=True).data
        representation['connections'] = ConnectionSerializer(instance.connections.all(), many=True).data

        return representation

    # Методы create и update не нужно переопределять вручную,
    # т.к. стандартный ModelSerializer обрабатывает ManyToMany поля с PrimaryKeyRelatedField(many=True) автоматически.