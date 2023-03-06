#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import date

from synopsis.tools import loggerSetup
from synopsis.common.config import BotAuth
from synopsis.db.database import DataBase

auth_conf = BotAuth()

if __name__ == '__main__':
    """Точка входа в программу.
    """
    # Версия бота
    bot_version = auth_conf.BOT_VERSION

    # Путь сохранения логов на удалённом сервере
    logger_path = f'../data/logs/{bot_version}-{date.today()}.log'
    # Инициализация и подключение глобального logger
    logger = loggerSetup.setup('logger', logger_path)

    logger.info('Program started.')

    # Подгрузка .env файла на windows
    # logger.info(f'Platform is {sys.platform}')
    # if sys.platform == "win32":
    #     from dotenv import load_dotenv
    #     load_dotenv()

    # Инициализация класса для подключение к базе данных
    db = DataBase()

    logger.info(f'Filesystem encoding: {sys.getfilesystemencoding()}, Preferred encoding: {locale.getpreferredencoding()}')
    logger.info(f'Current version {bot_version}')
    logger.info('Logging into Telegramm...')