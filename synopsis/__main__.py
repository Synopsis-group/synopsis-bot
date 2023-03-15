#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import date


from synopsis.tools import loggerSetup
from synopsis.config.settings import settings
from synopsis.db.database import DataBase
from synopsis.bot import botWorker

if __name__ == '__main__':
    """Точка входа в программу.
    """
    # Путь сохранения логов на удалённом сервере
    logger_path = f'../data/logs/{settings.bots.version}-{date.today()}.log'
    # Инициализация и подключение глобального logger
    logger = loggerSetup.setup('logger', logger_path)
    logger.info('Program started.')

    # Инициализация класса для подключение к базе данных
    db = DataBase()

    logger.info(f'Filesystem encoding: {sys.getfilesystemencoding()}, Preferred encoding: {locale.getpreferredencoding()}')
    logger.info(f'Current version {settings.bots.version}')
    logger.info('Logging into Telegramm...')

    botWorker.start()

