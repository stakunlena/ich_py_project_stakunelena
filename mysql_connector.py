# Модуль отвечающий за подключение к MySQL и содержащий функции поиска
 
import pymysql
from pymysql.cursors import DictCursor
from settings import MYSQL_SETTINGS
from logger import log_error # Функция логирования ошибок в файл

def connect_to_db():
    """
    Устанавливает соединение с базой данных MySQL (sakila)
    с использованием настроек из переменных среды.

    :return: объект соединения pymysql или None в случае ошибки.
    """
    try:
        connection = pymysql.connect(**MYSQL_SETTINGS, cursorclass=DictCursor)
        #print("Подключение к базе данных успешно.")
        return connection
    except pymysql.MySQLError as e:
        # print(f"Ошибка подключения к базе данных: {e}")
        msg = "Ошибка подключения к базе данных: {e}"
        print(msg)
        log_error(msg)
        return None
        
def search_by_keyword(keyword):
    """
    Выполняет поиск фильмов по части названия (ключевому слову) в базе MySQL.

    :param keyword: Ключевое слово для поиска в названии фильма.
    :return: Список словарей с информацией о фильмах (film_id, title, description, release_year).
             Если возникает ошибка — возвращается пустой список.
    """
    connection = connect_to_db()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT film_id, title, description, release_year
                FROM film
                WHERE title LIKE CONCAT('%%', %s, '%%')
                ORDER BY title;
            '''
            cursor.execute(sql, (keyword,))
            results = cursor.fetchall()
            return results  # возвращаем список результатов
    except pymysql.MySQLError as e:
        #print(f"Ошибка при выполнении запроса: {e}")
        msg = "Ошибка при выполнении запроса: {e}"
        print(msg)
        log_error(msg)        
        return []
    finally:
        connection.close()

def get_all_genres():
    """
    Получает список всех жанров из таблицы category базы данных MySQL.

    :return: Список словарей с полями 'category_id' и 'name'.
             В случае ошибки — пустой список.
    """
    connection = connect_to_db()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT category_id, name
                FROM category
                ORDER BY name;
            ''')
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        #print(f"Ошибка при получении жанров: {e}")
        msg = "Ошибка при получении жанров: {e}"
        print(msg)
        log_error(msg)           
        return []
    finally:
        connection.close()

def get_year_range_for_genre(category_id):
    """
    Возвращает минимальный и максимальный год выпуска фильмов для указанного жанра.

    :param category_id: Идентификатор жанра (категории).
    :return: Кортеж (min_year, max_year) или (None, None) в случае ошибки или отсутствия данных.
    """
    connection = connect_to_db()
    if connection is None:
        return None, None

    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT MIN(f.release_year), MAX(f.release_year)
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                WHERE fc.category_id = %s;
            ''', (category_id,))
            result = cursor.fetchone()
            return result['MIN(f.release_year)'], result['MAX(f.release_year)']
    except pymysql.MySQLError as e:
        #print(f"Ошибка при получении диапазона годов: {e}")
        msg = "Ошибка при получении диапазона годов: {e}"
        print(msg)
        log_error(msg)              
        return None, None
    finally:
        connection.close()

def search_by_genre_and_years(category_id, year_from, year_to):
    """
    Выполняет поиск фильмов по жанру и диапазону годов выпуска.

    :param category_id: Идентификатор жанра.
    :param year_from: Начальный год диапазона.
    :param year_to: Конечный год диапазона.
    :return: Список фильмов в формате словарей (film_id, title, description, release_year).
             В случае ошибки — пустой список.
    """
    connection = connect_to_db()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT f.film_id, f.title, f.description, f.release_year
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                WHERE fc.category_id = %s
                AND f.release_year BETWEEN %s AND %s
                ORDER BY f.title;
            ''', (category_id, year_from, year_to))
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        #print(f"Ошибка при поиске фильмов: {e}")
        msg = "Ошибка при поиске фильмов: {e}"
        print(msg)
        log_error(msg)        
        return []
    finally:
        connection.close()
