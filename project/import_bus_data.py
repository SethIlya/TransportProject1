# project/management/commands/import_bus_data.py

import os
import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from project.models import Route, Vehicle, VehiclePosition, TransportType

class Command(BaseCommand):
    help = 'Импортирует данные о положении автобусов из JSON файлов, отсортированных по маршрутам.'

    def add_arguments(self, parser):
        parser.add_argument('json_dir', type=str, help='Путь к директории с JSON файлами (например, sorted_routes)')

    def handle(self, *args, **options):
        json_dir = Path(options['json_dir'])
        if not json_dir.is_dir():
            raise CommandError(f"Директория не найдена: {json_dir}")

        # Получаем или создаем дефолтный тип транспорта "Автобус"
        transport_type, _ = TransportType.objects.get_or_create(name='Автобус')

        files_to_process = list(json_dir.glob('route_*.json'))
        total_files = len(files_to_process)
        self.stdout.write(f"Найдено {total_files} файлов для обработки.")

        for i, file_path in enumerate(files_to_process):
            self.stdout.write(f"\n--- Обработка файла [{i+1}/{total_files}]: {file_path.name} ---")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                bus_data_list = data.get('bus_data', [])
                if not bus_data_list:
                    self.stdout.write(self.style.WARNING("Файл не содержит 'bus_data' или список пуст. Пропускаем."))
                    continue
                
                # Получаем или создаем маршрут
                route_id = data.get('route_id')
                route_name = data.get('route_name', f"Маршрут {route_id}")
                
                route, created = Route.objects.get_or_create(
                    id=route_id,
                    defaults={'name': route_name, 'transport_type': transport_type}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Создан новый маршрут: {route.name} (ID: {route.id})"))

                positions_to_create = []
                processed_vehicles = set()

                for item in bus_data_list:
                    gos_num = item.get('gos_num')
                    if not gos_num:
                        continue
                    
                    # Получаем или создаем ТС
                    vehicle, _ = Vehicle.objects.get_or_create(gos_num=gos_num)
                    processed_vehicles.add(vehicle.id)

                    # Преобразуем координаты
                    try:
                        raw_lat, raw_lon = float(item['lat']), float(item['lon'])
                        real_lat = (raw_lat / 1571673) - 0.002005
                        real_lon = (raw_lon / 1467000) - 0.002415
                    except (ValueError, TypeError, KeyError) as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка конвертации координат для {gos_num}: {e}"))
                        continue

                    # Преобразуем время
                    try:
                        timestamp_str = item.get('lasttime')
                        # Указываем Django, что это время уже в нашем часовом поясе (Asia/Irkutsk)
                        timestamp = make_aware(datetime.strptime(timestamp_str, "%d.%m.%Y %H:%M:%S"))
                    except (ValueError, TypeError) as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка конвертации времени для {gos_num}: {e}"))
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

                # Используем bulk_create для массовой и быстрой вставки
                if positions_to_create:
                    with transaction.atomic():
                        # ignore_conflicts=True пропустит записи, которые нарушают unique_together
                        # (т.е. если позиция для этого ТС в это время уже есть в БД)
                        VehiclePosition.objects.bulk_create(positions_to_create, ignore_conflicts=True)
                    self.stdout.write(self.style.SUCCESS(f"Загружено {len(positions_to_create)} записей о позициях для {len(processed_vehicles)} ТС."))

            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"Не удалось прочитать JSON из файла: {file_path.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Произошла непредвиденная ошибка при обработке файла {file_path.name}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("\nИмпорт завершен."))