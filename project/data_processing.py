import os
import json
import random
import requests
import time
from datetime import datetime
from pathlib import Path
from .services import import_bus_data_from_files
from collections import defaultdict

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


BASE_URL = "http://irkbus.ru/php/getVehiclesMarkers.php"
MAIN_PAGE_URL = "http://irkbus.ru/"

PARAMS = {
    "rids": "2-1,13-1,1-1,14-1,19-0,20-0,15-1,16-1,3-1,4-1,344-0,343-0,17-1,5-1,18-1,233-0,232-0,6-0,5-0,19-1,8-1,9-1,20-1,348-0,347-0,11-1,10-1,202-0,201-0,84-0,83-0,1-0,2-0,395-0,394-0,6-1,7-1,129-0,128-0,17-0,18-0,214-0,215-0,12-1,24-0,23-0,12-0,11-0,4-0,3-0,62-0,63-0,9-0,10-0,61-0,60-0,308-0,309-0,26-0,25-0,296-0,297-0,242-0,243-0,16-0,15-0,13-0,14-0,65-0,64-0,346-0,69-0,68-0,27-0,28-0,72-0,73-0,53-0,52-0,279-0,278-0,37-0,36-0,235-0,234-0,228-0,229-0,127-0,126-0,299-0,298-0,301-0,300-0,78-0,77-0,124-0,125-0,82-0,81-0,80-0,79-0,303-0,302-0,30-0,31-0,222-0,223-0,207-0,206-0,224-0,225-0,209-0,208-0,351-0,350-0,425-0,424-0,353-0,352-0,241-0,240-0,286-0,287-0,226-0,227-0,210-0,211-0,216-0,217-0,218-0,219-0,419-0,420-0,43-0,42-0,396-0,397-0,422-0,421-0,408-0,423-0,355-0,354-0,237-0,236-0,221-0,220-0,327-0,326-0,48-0,49-0,313-0,312-0,45-0,44-0,305-0,304-0,345-0,426-0,46-0,47-0,291-0,290-0,33-0,32-0,213-0,212-0,316-0,315-0,203-0,38-0,230-0,231-0,323-0,324-0,123-0,391-0,390-0,393-0,392-0,359-0,358-0,363-0,362-0,365-0,364-0,369-0,368-0,367-0,366-0,389-0,388-0,370-0,371-0,373-0,372-0,374-0,375-0,376-0,377-0,402-0,403-0,417-0,418-0,378-0,379-0,380-0,381-0,406-0,407-0,382-0,383-0,386-0,387-0,405-0,404-0,357-0,356-0,66-0,67-0,334-0,333-0,415-0,416-0",
    "lat0": 0, "lng0": 0, "lat1": 90, "lng1": 180, "curk": 0, "city": "irkutsk", "info": 12345, "_": None
}
HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'irkbus.ru',
    'Referer': 'http://irkbus.ru/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': '__ga=GA1.2.1772930182.1747628825; PHPSESSID=95rs0s8i1rsegff8h3v286hlk7; _gid=GA1.2.1675765423.1765710345; _ga_1333VHZZJ1=GS2.2.s1765710346$o9$g0$t1765710346$j60$l0$h0'
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data_processing_files'
FULL_DATA_PATH = DATA_DIR / 'full_data.json'
DEDUPLICATED_PATH = DATA_DIR / 'deduplicated_data.json'
SORTED_DIR = DATA_DIR / 'sorted_routes'

def run_parser(duration_seconds=300):
    print(f"[Парсер] Запуск на {duration_seconds} секунд...")
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    
    session.mount('http://', HTTPAdapter(max_retries=retries))
    
    session.headers.update(HEADERS)
    start_time = time.time()
    
    try:
        print("[Парсер] Получение свежей сессии (Cookie)...")
        session.get(MAIN_PAGE_URL, timeout=10)
    except requests.RequestException as e:
        print(f"[Парсер] Не удалось получить Cookie, работа будет продолжена. Ошибка: {e}")
        
    if FULL_DATA_PATH.exists():
        FULL_DATA_PATH.unlink()

    while time.time() - start_time < duration_seconds:
        try:
            PARAMS["_"] = int(datetime.now().timestamp() * 1000)
            response = session.get(BASE_URL, params=PARAMS, timeout=15)
            response.raise_for_status() # Проверяем, что ответ успешный (не 4xx или 5xx)

            data = response.json()
            if data.get("anims"):
                with open(FULL_DATA_PATH, "a", encoding="utf-8") as f:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
                print(f"[Парсер] {datetime.now().strftime('%H:%M:%S')}: Получены и сохранены данные.")
            
            time.sleep(10 + random.randint(0, 5))
            
        except requests.exceptions.RequestException as e:
            print(f"[Парсер] Критическая ошибка сети после нескольких попыток: {e}")
            print("[Парсер] Пропускаем итерацию, попробуем снова через 20 секунд.")
            time.sleep(20)
        except Exception as e:
            print(f"[Парсер] Неизвестная ошибка в цикле: {e}")
            time.sleep(15)
            
    print("[Парсер] Работа завершена.")

def remove_duplicates():
    print("[Очистка] Удаление дубликатов...")
    unique_objects = {}
    if not FULL_DATA_PATH.exists():
        print("[Очистка] Файл с сырыми данными не найден. Пропускаем шаг.")
        return

    with open(FULL_DATA_PATH, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                data = json.loads(line.strip())
                data_str = json.dumps(data, sort_keys=True)
                if data_str not in unique_objects:
                    unique_objects[data_str] = data
            except json.JSONDecodeError:
                continue

    sorted_data = sorted(unique_objects.values(), key=lambda obj: obj.get('maxk', 0))

    with open(DEDUPLICATED_PATH, 'w', encoding='utf-8') as outfile:
        for obj in sorted_data:
            outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print("[Очистка] Дубликаты удалены, результат сохранен.")

def sort_by_route():
    print("[Сортировка] Сортировка по маршрутам...")
    if not DEDUPLICATED_PATH.exists():
        print("[Сортировка] Файл с очищенными данными не найден. Пропускаем шаг.")
        return

    routes_data = defaultdict(list)

    with open(DEDUPLICATED_PATH, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                data = json.loads(line.strip())
                for bus in data.get("anims", []):
                    route_id = bus.get("rid")
                    if route_id is not None:
                        routes_data[route_id].append(bus)
            except json.JSONDecodeError:
                continue
    
    # Очищаем старые файлы перед созданием новых
    if SORTED_DIR.exists():
        for f in SORTED_DIR.glob('*.json'):
            f.unlink()
    
    SORTED_DIR.mkdir(exist_ok=True)

    for route_id, bus_list in routes_data.items():
        output_filename = SORTED_DIR / f"route_{route_id}.json"
        final_route_data = {
            "route_id": route_id,
            "route_name": bus_list[0].get("rnum", f"Маршрут {route_id}"),
            "bus_data": bus_list
        }
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            json.dump(final_route_data, outfile, ensure_ascii=False, indent=4)
    print(f"[Сортировка] Данные отсортированы по {len(routes_data)} маршрутам.")

def run_collection_pipeline(parse_duration_seconds=300):

    
    DATA_DIR.mkdir(exist_ok=True)
    
    run_parser(parse_duration_seconds)
    
    remove_duplicates()

    sort_by_route()


def run_import_pipeline():


    print("[Импорт] Запуск импорта в базу данных...")
    if SORTED_DIR.exists():
        files_to_import = list(SORTED_DIR.glob('*.json'))
        if files_to_import:
            print(f"[Импорт] Найдено файлов для импорта: {len(files_to_import)}")
            file_streams = [open(path, 'rb') for path in files_to_import]
            try:
                result = import_bus_data_from_files(file_streams)
                print(f"[Импорт] Завершено. Создано новых записей: {result['total_positions_created']}")
                if result['errors']:
                    print("[Импорт] Ошибки:")
                    for error in result['errors']:
                        print(f" - {error}")
            finally:
                for stream in file_streams:
                    stream.close()
        else:
            print("[Импорт] Не найдено файлов для импорта в папке 'sorted_routes'.")
    else:
        print("[Импорт] Директория 'sorted_routes' не найдена. Сначала нужно запустить сбор данных.")
