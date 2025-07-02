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
