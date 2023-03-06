#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import date

from synopsis.tools import loggerSetup

if __name__ == '__main__':
    """Точка входа в программу.
    """
    # Путь сохранения логов на удалённом сервере
    logger_path = f'../data/logs/{date.today()}.log'
    # Инициализация и подключение глобального logger
    logger = loggerSetup.setup('logger', logger_path)

    logger.info('Program started.')

    # Подгрузка .env файла на windows
    logger.info(f'Platform is {sys.platform}')
    if sys.platform == "win32":
        from dotenv import load_dotenv
        load_dotenv()

    # Инициализация класса для подключение к базе данных
    # db = DataBase()

    logger.info(f'Filesystem encoding: {sys.getfilesystemencoding()}, Preferred encoding: {locale.getpreferredencoding()}')