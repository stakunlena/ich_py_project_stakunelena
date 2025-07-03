
#Модуль содержит обработчики основных команд приложения

from mongodb_connector import *
from mysql_connector import *
from logger import log_error # Функция логирования ошибок в файл

# обработка первого пункта меню

def handle_keyword_search():
    """
    Обрабатывает поиск фильмов по ключевому слову.

    1. Запрашивает у пользователя ключевое слово.
    2. Выполняет поиск по части названия фильма в базе MySQL.
    3. Логирует запрос в MongoDB.
    4. Постранично отображает найденные фильмы по 10 результатов за раз.
    """
    print("\n== ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ ==")
    keyword = input("Введите слово или название фильма (или 0 для возврата): ")
    if keyword == "0":
        return

    print(f"Выполняется поиск по ключевому слову: {keyword}...\n")
    results = search_by_keyword(keyword)

    # Логирование запроса в MongoDB с новой структурой
    log_search_to_mongo(
        search_type="keyword",
        params={
            "keyword": keyword,
            "year_from": None,
            "year_to": None,
            "genre_id": None,
            "genre_name": None
        },
        results_count=len(results)
    )

    if not results:
        print("Ничего не найдено.\n")
        return

    index = 0
    page_size = 10
    total = len(results)

    while index < total:
        page = results[index:index + page_size]
        for film in page:
            print(f"{film['film_id']}. {film['title']} ({film['release_year']})")
            print(f"Описание: {film['description']}\n")

        index += page_size

        if index < total:
            more = input("Показать следующие 10 результатов? (y/n): ").lower()
            if more != 'y':
                break
        else:
            print("Это были все результаты.\n")


# обработка второго пункта меню

def handle_genre_search():
    """
    Обрабатывает поиск фильмов по выбранному жанру и диапазону годов.

    Шаги:
    1. Отображает список всех доступных жанров.
    2. Пользователь выбирает жанр.
    3. Отображает допустимый диапазон годов.
    4. Пользователь вводит год или диапазон годов.
    5. Выполняется поиск фильмов в базе MySQL.
    6. Результаты логируются в MongoDB.
    7. Результаты отображаются постранично (по 10 записей).
    """
    while True:
        print("\n== ДОСТУПНЫЕ ЖАНРЫ ==")
        genres = get_all_genres()
        for g in genres:
            print(f"{g['category_id']}. {g['name']}")
        print("-------------------------------\n0. Вернуться в меню")

        genre_input = input("\nВыберите номер жанра: ")
        if genre_input == "0":
            return

        if not genre_input.isdigit():
            print("Ошибка: введите число.")
            continue

        genre_id = int(genre_input)
        genre_names = {g['category_id']: g['name'] for g in genres}
        if genre_id not in genre_names:
            print("Ошибка: такого жанра нет.")
            continue

        min_year, max_year = get_year_range_for_genre(genre_id)
        if min_year is None:
            print("Нет фильмов в этом жанре.")
            continue

        print(f"Доступный диапазон: {min_year} - {max_year}")
        print("0. Вернуться к выбору жанра")

        while True:
            year_input = input("Введите год или диапазон (например: 2005 или 2005-2010): ")
            if year_input == "0":
                break

            if '-' in year_input:
                parts = year_input.split('-')
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    print("Ошибка: неверный формат.")
                    continue
                year_from, year_to = int(parts[0]), int(parts[1])
            elif year_input.isdigit():
                year_from = year_to = int(year_input)
            else:
                print("Ошибка: введите год в формате yyyy или yyyy-yyyy")
                continue

            results = search_by_genre_and_years(genre_id, year_from, year_to)

            # логирование в MongoDB
            log_search_to_mongo(
                search_type="genre_year",
                params={
                    "genre_id": genre_id,
                    "genre_name": genre_names[genre_id],
                    "year_from": year_from,
                    "year_to": year_to
                },
                results_count=len(results)
            )

            if not results:
                print("Фильмы не найдены.")
                continue

            index = 0
            page_size = 10
            while index < len(results):
                page = results[index:index + page_size]
                for film in page:
                    print(f"{film['film_id']} | {film['title']} ({film['release_year']})")
                    print(f"Описание: {film['description']}\n")

                index += page_size
                if index >= len(results):
                    print("Это были все результаты.")
                    break

                cont = input("Показать следующие 10? (y/n): ").strip().lower()
                if cont != 'y':
                    break
            break

# обработка третьего пункта меню

def show_top_5_keyword_queries():
    """
    Выводит топ-5 наиболее частых поисковых запросов по ключевому слову.

    Обрабатывает исключения при получении статистики из MongoDB
    и записывает сообщение об ошибке в лог.
    """
    print("\n== ТОП-5 ПОПУЛЯРНЫХ ЗАПРОСОВ ==")
    try:
        get_most_frequent_queries()
    except Exception as e:
        # print(f"Ошибка при получении статистики: {e}")
        error_msg = f"Ошибка при получении статистики: {e}"
        print(error_msg)
        log_error(error_msg)


def show_last_5_keyword_queries():
    """
    Выводит последние 5 поисковых запросов по ключевому слову.

    При возникновении ошибки выводит сообщение и логирует его.
    """
    print("\n== ПОСЛЕДНИЕ 5 ПОИСКОВЫХ ЗАПРОСОВ ==")
    try:
        get_last_queries(limit=5)
    except Exception as e:
        #print(f"Ошибка при получении последних запросов: {e}")
        error_msg = f"Ошибка при получении последних запросов: {e}"
        print(error_msg)
        log_error(error_msg)

   
def show_recent_query_logs():
    """
    Выводит все поисковые запросы, сохранённые в MongoDB, постранично по 10 записей.

    Отображаются поля:
    - timestamp (время запроса),
    - search_type (тип запроса),
    - params (параметры поиска),
    - results_count (кол-во результатов).

    В конце каждой страницы пользователь может выбрать продолжение просмотра.
    """
    print("\n== СПИСОК ВСЕХ ПОИСКОВЫХ ЗАПРОСОВ (ПО 10 НА СТРАНИЦЕ) ==")

    client, collection = connect_to_mongo()

    try:
        cursor = collection.find().sort("timestamp", -1)
        results = list(cursor)
        if not results:
            print("Нет сохранённых запросов.\n")
            return

        index = 0
        page_size = 10
        total = len(results)

        while index < total:
            page = results[index:index + page_size]
            for doc in page:
                timestamp = doc.get("timestamp", "N/A")
                search_type = doc.get("search_type", "N/A")
                params = doc.get("params", {})
                results_count = doc.get("results_count", "N/A")

                print(f"[{timestamp}] {search_type.upper()} — {params} (результатов: {results_count})")

            index += page_size

            if index < total:
                cont = input("\nПоказать ещё 10 запросов? (y/n): ").strip().lower()
                if cont != "y":
                    break
            else:
                print("\nЭто были все запросы.\n")

    finally:
        client.close()

