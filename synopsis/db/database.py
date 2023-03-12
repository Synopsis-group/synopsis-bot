#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import random, string
from os.path import realpath, dirname
import psycopg2
from psycopg2 import Error, sql

from synopsis.common import config

logger = logging.getLogger('logger')
db_conf = config.Database()

class DataBase():
    """Интерфейс для работы с базой данных PostgreSql.
    """
    def __init__(self):
        """Инициализация класса DataBase.
        """
        # Инициализация объекта подключения
        self.conn = None
        self.connect_db()

    #Подключение к базе данных
    def connect_db(self):
        """Подключение к базе данных.
        """
        try:
            logger.debug(f'Connecting to {db_conf.DB_NAME}')
            self.conn = psycopg2.connect(
                user     = db_conf.PG_USER,
                password = db_conf.PG_PASSWORD,
                host     = db_conf.PG_HOST,
                port     = db_conf.PG_PORT,
                database = db_conf.DB_NAME)
            self.conn.autocommit=True
        except (Exception, Error) as er:
            logger.error(f'Connection to database failed: {er}')
            logger.debug('Closing the program...')
            sys.exit()
        else:
            logger.debug('Database was connected successfully')
            self.create_tables()

    #Создание таблиц, если они отсутствуют
    def create_tables(self):
        """Создание необходимых таблиц в случае их отсутствия.
        """
        try:
            with self.conn.cursor() as curs:
                curs.execute(open(realpath(dirname(__file__) + "/scripts/init_tables.sql"), "r").read())

        except (Exception, Error) as er:
            #Закрытие освобождение памяти + выход из программы для предотвращения рекурсии и настройки PostgreSQL на хосте
            logger.error(f'Tables creation failed: {er}')
            if self.conn:
                self.conn.close()
                logger.debug('Connection was closed')
            logger.debug('Closing the program...')
            sys.exit()
        else:
            logger.debug(f'Tables are ready to use')

    def _generateEventId(self):
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(6))

    def insert_data_event(self, data: list) -> bool:
        """Inserting new data about event into database TABLE events.

        Args:
            data (list): Data of event (event_id, event_status, author_id, title, event_type, start_time,
                                    event_date, duration, organization)

        Returns:
            bool: Status of operation.
        """
        try:
            insert_query = sql.SQL('INSERT INTO events (event_id, event_status, author_id, title, event_type, start_time, event_date, duration, organization) VALUES ({})').format(
                sql.SQL(', ').join(map(sql.Literal, [self._generateEventId()] + data)))

            with self.conn.cursor() as curs:
                curs.execute(insert_query)

        except (Exception, Error) as er:
            logger.error(f"Can't insert query into database: {er}")
            return False
        else:
            logger.debug(f"Data was successfully inserted!")
            return True

    def update_data_event(self, event_id: str, editor_id: int, data: dict) -> bool:
        """Updating data of event in database.

        Args:
            event_id (str): Event id.
            editor_id (int): Editor id.
            data (dict): Dictionary with new data.

        Returns:
            bool: Status of operation.
        """
        try:
            params = [sql.SQL('=').join([sql.Identifier(key), sql.Literal(value)]) for key, value in data.items()]
            insert_query = sql.SQL('UPDATE events SET changed_date=CURRENT_TIMESTAMP, editor_id=%s, {} WHERE event_id=%s').format(sql.SQL(', ').join(params))

            with self.conn.cursor() as curs:
                curs.execute(insert_query, (editor_id, event_id))

        except (Exception, Error) as er:
            logger.error(f"Can't update query in database: {er}")
            return False
        else:
            logger.debug(f"Data was successfully updated!")
            return True

    def get_events(self, filters: dict) -> list:
        """Gettings info about events by filters.

        Args:
            filters (dict): Filters.

        Returns:
            list: Available events.
        """
        try:
            params = [sql.SQL('=').join([sql.Identifier(key), sql.Literal(value)]) for key, value in filters.items()]
            insert_query = sql.SQL('SELECT * FROM events WHERE {}').format(sql.SQL(' AND ').join(params))

            events = []
            with self.conn.cursor() as curs:
                curs.execute(insert_query)
                events = curs.fetchall()

        except (Exception, Error) as er:
            logger.error(f"Can't get events: {er}")
            return None
        else:
            logger.debug(f"Events were successfully got!")
            return events