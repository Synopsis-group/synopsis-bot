#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import date

from synopsis.tools import loggerSetup
from synopsis.common.config import BotAuth
from synopsis.db.database import DataBase
from synopsis.common.config import EventDate, EventDuration, EventStatus, EventTime, EventType
# from synopsis.bot import tgWorker

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

    # db.insert_data_event([EventStatus.NEW.value, 1234, "Event new", EventType.SPORT.value, EventTime.BEFORE_MIDDAY.value, EventDate.TODAY.value, EventDuration.HALF_HOUR.value, "дюсш 2"])

    # new_data = { 'title': 'Клатч', 'event_type': EventType.SPORT.value }
    # db.update_data_event('qjuy8l', 7878, new_data)

    # filters = {'author_id': 23418793, 'event_status': EventStatus.CHANGED.value}
    # logger.debug(db.get_events(filters))

    # tgWorker.start()

