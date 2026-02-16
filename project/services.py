import json
import zipfile
from io import TextIOWrapper
from datetime import datetime

from django.db import transaction
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from .models import Route, Vehicle, VehiclePosition, TransportType

RTYPE_MAP = {
    'А': 'Автобус',
    'Т': 'Троллейбус',
    'Тр': 'Трамвай',
}

def _process_single_json_stream(content_stream):
    """
    Внутренняя helper-функция для обработки одного потока с JSON-данными.
    Определяет тип транспорта, создает/обновляет маршрут и готовит данные о позициях.
    """
    positions_to_create = []
    
    try:
        data = json.load(content_stream)
    except json.JSONDecodeError:
        return [], "Некорректный формат JSON."

    bus_data_list = data.get('bus_data', [])
    if not bus_data_list:
        return [], "Файл не содержит ключ 'bus_data' или этот список пуст."

    first_bus = bus_data_list[0]
    rtype = first_bus.get('rtype', 'А') # По умолчанию считаем, что это автобус
    transport_type_name = RTYPE_MAP.get(rtype, 'Автобус') # Ищем в словаре, иначе - Автобус
    
    transport_type, _ = TransportType.objects.get_or_create(name=transport_type_name)

    route_id = data.get('route_id')
    route_name = data.get('route_name', f"Маршрут {route_id}")
    
    if not route_id:
        return [], "В файле отсутствует 'route_id'."
    
    route, created = Route.objects.get_or_create(
        id=route_id,
        defaults={'name': route_name, 'transport_type': transport_type}
    )
    if not created and route.transport_type != transport_type:
        route.transport_type = transport_type
        route.save()

    for item in bus_data_list:
        gos_num = item.get('gos_num')
        if not gos_num:
            continue

        vehicle, _ = Vehicle.objects.get_or_create(gos_num=gos_num)

        try:
            # Преобразуем данные в нужные форматы
            raw_lat, raw_lon = float(item['lat']), float(item['lon'])
            real_lat = (raw_lat / 1571673) - 0.002005
            real_lon = (raw_lon / 1467000) - 0.002415
            timestamp_str = item.get('lasttime')
            timestamp = make_aware(datetime.strptime(timestamp_str, "%d.%m.%Y %H:%M:%S"))
        except (ValueError, TypeError, KeyError):
            continue

        positions_to_create.append(
            VehiclePosition(
                vehicle=vehicle, 
                route=route, 
                timestamp=timestamp,
                location=Point(real_lon, real_lat, srid=4326),
                speed=item.get('speed', 0), 
                direction=item.get('dir', 0)
            )
        )
    
    return positions_to_create, None

def import_bus_data_from_files(files):
    """
    Основная сервисная функция. Принимает список загруженных файлов,
    обрабатывает .json и .zip, загружает данные в БД.
    """
    total_positions_created = 0
    errors = []
    
    positions_to_bulk_create = []

    for uploaded_file in files:
        try:
            # Обработка ZIP-архивов
            if uploaded_file.name.lower().endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zf:
                    for filename in zf.namelist():
                        if filename.lower().endswith('.json') and not filename.startswith('__MACOSX'):
                            with zf.open(filename, 'r') as json_file:
                                positions, err = _process_single_json_stream(TextIOWrapper(json_file, 'utf-8'))
                                if err:
                                    errors.append(f"{uploaded_file.name}/{filename}: {err}")
                                else:
                                    positions_to_bulk_create.extend(positions)
            elif uploaded_file.name.lower().endswith('.json'):
                uploaded_file.seek(0)
                positions, err = _process_single_json_stream(TextIOWrapper(uploaded_file, 'utf-8'))
                if err:
                    errors.append(f"{uploaded_file.name}: {err}")
                else:
                    positions_to_bulk_create.extend(positions)
            else:
                errors.append(f"{uploaded_file.name}: Неподдерживаемый формат (нужен .zip или .json).")
        except Exception as e:
            errors.append(f"Критическая ошибка при обработке файла {uploaded_file.name}: {e}")

    if positions_to_bulk_create:
        with transaction.atomic():
            created_objects = VehiclePosition.objects.bulk_create(positions_to_bulk_create, ignore_conflicts=True)
            total_positions_created = len(created_objects)

    return {
        "message": "Импорт завершен.",
        "total_positions_created": total_positions_created,
        "errors": errors
    }