# Модуль логирования ошибок приложения в csv файл

import csv
import os
from datetime import datetime


def log_error(error_msg: str) -> None:
    """
    Сохраняет сообщение об ошибке в CSV-файл 'error_log.csv'.

    Каждая запись содержит временную метку и текст ошибки.
    Если файл не существует, создается с заголовком.
    
    :param error_msg: Сообщение об ошибке для записи в журнал.
    """
    log_file = os.path.join(os.getcwd(), "error_log.csv")
    file_exists = os.path.isfile(log_file)

    try:
        with open(log_file, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["timestamp", "error_message"])
            writer.writerow([datetime.now().isoformat(timespec='seconds'), error_msg])
    except Exception as file_error:
        print(f"[Ошибка логирования] {file_error}")
