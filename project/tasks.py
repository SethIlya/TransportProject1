# project/tasks.py

from .data_processing import run_collection_pipeline, run_import_pipeline

def run_collection_task():
    """
    Фоновая задача ТОЛЬКО для сбора, очистки и сортировки данных по файлам.
    """
    print("Начало фоновой задачи: СБОР ДАННЫХ...")
    run_collection_pipeline(parse_duration_seconds=300)
    print("Фоновая задача СБОРА ДАННЫХ завершена.")


def run_import_task():
    """
    Фоновая задача ТОЛЬКО для импорта уже собранных файлов в базу данных.
    """
    print("Начало фоновой задачи: ИМПОРТ В БД...")
    run_import_pipeline()
    print("Фоновая задача ИМПОРТА В БД завершена.")