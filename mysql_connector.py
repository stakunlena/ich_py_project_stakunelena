"""
Модуль отвечающий за подключение к MySQL и содержащий функции поиска
"""
import pymysql
from pymysql.cursors import DictCursor
from settings import MYSQL_SETTINGS
from logger import log_error # Функция логирования ошибок в файл

def connect_to_db():
    '''
    Устанавливает соединение с базой данных sakila с использованием PyMySQL.
    Возвращает объект соединения или None в случае ошибки.
    '''
    
    """
    try:
        load_dotenv() # Временно. Загружаем переменные среды
    except:
        print('Не удалось загрузить переменные среды')
    
    config = {
        'host': os.getenv('MYSQL_HOST'), # Загружаем значение из переменной окружения MYSQL_HOST
        'user': os.getenv('MYSQL_USER'), # Загружаем значение из переменной окружения MYSQL_USER
        'password': os.getenv('MYSQL_PASSWORD'), # Загружаем значение из переменной окружения MYSQL_PASSWORD
        'database': os.getenv('MYSQL_DATABASE'), # Загружаем значение из переменной окружения MYSQL_DATABASE
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
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

##обработка второго пункта меню
def get_all_genres():
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
