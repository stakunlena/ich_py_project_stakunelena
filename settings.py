"""
Модуль, хранящий настройки приложения
"""

from dotenv import load_dotenv
import os

load_dotenv()  # Загружаем переменные среды из файла .env

MYSQL_SETTINGS = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
}

MONGODB_SETTINGS = {
    'user': os.getenv('MONGO_USER'),
    'password': os.getenv('MONGO_PASSWORD'),
    'host': os.getenv('MONGO_HOST'),
    'db': os.getenv('MONGO_DB'),
    'collection': os.getenv('MONGO_COLLECTION'),
    'uri': (
        f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}"
        f"@{os.getenv('MONGO_HOST')}/?authSource={os.getenv('MONGO_DB')}"
        f"&readPreference=primary&ssl=false&authMechanism=DEFAULT"
    )
}