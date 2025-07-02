from pymongo import MongoClient, errors
from settings import MONGODB_SETTINGS
""" Временно, до вынесения функций в отдельный модуль
from pymongo.collection import Collection
from datetime import datetime
from typing import Optional
"""

def connect_to_mongo():
    """Устанавливает и возвращает соединение с коллекцией MongoDB."""
    try:
        client = MongoClient(MONGODB_SETTINGS['uri'])
        db = client[MONGODB_SETTINGS['db']]
        collection = db[MONGODB_SETTINGS['collection']]
        return client, collection
    except errors.ConnectionFailure:
        print("Ошибка подключения к MongoDB")
    except errors.OperationFailure:
        print("Ошибка авторизации или запроса")

def log_search_to_mongo(search_type: str, params: dict, results_count: int):
    """Записывает структуру запроса в коллекцию MongoDB."""
    client, collection = connect_to_mongo()

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "search_type": search_type,
        "params": params,
        "results_count": results_count
    }

    result = collection.insert_one(log_entry)
    print(f"Log inserted with ID: {result.inserted_id}")

    client.close()
    
def clear_log_collection():
    """Очищает коллекцию final_project_100125_stakun_elena."""
    client, collection = connect_to_mongo()
    result = collection.delete_many({})
    print(f"{result.deleted_count} documents deleted from the collection.")
    client.close()

def get_most_frequent_queries() -> None:
    """
    Выводит 5 наиболее частых поисковых запросов по ключевому слову из MongoDB.
    """
    client, collection = connect_to_mongo()  # type: (MongoClient, Collection)

    pipeline: list[dict] = [
        {"$match": {"search_type": "keyword"}},
        {"$group": {"_id": "$params.keyword", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]

    results: list[dict] = list(collection.aggregate(pipeline))
    client.close()

    if not results:
        print("Нет популярных запросов.")
    else:
        print("Топ-5 популярных запросов по ключевым словам:")
        for entry in results:
            print(f"- {entry['_id']} (встречается {entry['count']} раз)")


def get_last_queries(limit: int = 5) -> None:
    """
    Выводит последние N поисковых запросов по ключевому слову из MongoDB.

    :param limit: Количество последних записей для отображения (по умолчанию 5)
    """
    client, collection = connect_to_mongo()  # type: (MongoClient, Collection)

    results: list[dict] = list(collection.find({"search_type": "keyword"})
                               .sort("timestamp", -1)
                               .limit(limit))

    client.close()

    if not results:
        print("История пуста.")
    else:
        print(f"Последние {limit} запросов:")
        for entry in results:
            keyword: Optional[str] = entry.get("params", {}).get("keyword", "")
            ts: Optional[str] = entry.get("timestamp", "")
            print(f"- {keyword} (время: {ts})")