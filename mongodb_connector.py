# Модуль отвечающий за подключение к MongoDB и содержащий функции логирования запросов пользователя и статистики

from pymongo import MongoClient, errors
from settings import MONGODB_SETTINGS
from datetime import datetime
from logger import log_error # Функция логирования ошибок в файл


def connect_to_mongo():
    """
    Устанавливает соединение с MongoDB и возвращает клиент и коллекцию.

    :return: Кортеж (client, collection) при успешном подключении,
             иначе None в случае ошибки.
    """
    try:
        client = MongoClient(MONGODB_SETTINGS['uri'])
        db = client[MONGODB_SETTINGS['db']]
        collection = db[MONGODB_SETTINGS['collection']]
        return client, collection
    except errors.ConnectionFailure as e:
        msg = f"Ошибка подключения к MongoDB: {e}"
        print(msg)
        log_error(msg)
    except errors.OperationFailure as e:
        msg = f"Ошибка авторизации или запроса в MongoDB: {e}"
        print(msg)
        log_error(msg)
        
def log_search_to_mongo(search_type: str, params: dict, results_count: int):
    """
    Записывает информацию о поисковом запросе в коллекцию MongoDB.

    :param search_type: Тип поиска ('keyword' или 'genre_year').
    :param params: Параметры поиска (ключевое слово, жанр, годы и т.п.).
    :param results_count: Количество найденных результатов.
    """
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
    """
    Очищает коллекцию MongoDB final_project_100125_stakun_elena, удаляя все документы.

    Используется для удаления всей истории поисковых запросов.
    """
    client, collection = connect_to_mongo()
    result = collection.delete_many({})
    print(f"{result.deleted_count} documents deleted from the collection.")
    client.close()

def get_most_frequent_queries() -> None:
    """
    Выводит 5 наиболее частых поисковых запросов по ключевому слову из MongoDB.

    Использует агрегирующий pipeline для подсчета частоты запросов.
    В случае ошибки выводит сообщение и записывает лог.
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