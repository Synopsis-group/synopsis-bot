#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import random, string
from os.path import realpath, dirname
import psycopg2
from psycopg2 import Error, sql
from environs import Env

from synopsis.config.settings import settings
from synopsis.config.users import users

logger = logging.getLogger('logger')

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
            logger.debug(f'Connecting to {settings.db.name}')
            self.conn = psycopg2.connect(
                user     = settings.db.user,
                password = settings.db.password,
                host     = settings.db.host,
                port     = settings.db.port,
                database = settings.db.name)
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
            env = Env()
            env.read_env()
            for user_obj in env.list('OWNERS_ID', delimiter=',', subcast=str):
                user_id, username = user_obj.split(' ')
                if self.get_user(user_id): continue
                logger.debug(f"Insert new user {user_id} ({username}) as owner")
                self.insert_user([user_id, username, users.owner.value])

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
            insert_query = sql.SQL('INSERT INTO events (event_id, event_status, author_id, username, title, event_type, start_time, event_date, duration, organization) VALUES ({})').format(
                sql.SQL(', ').join(map(sql.Literal, [self._generateEventId()] + data)))

            with self.conn.cursor() as curs:
                curs.execute(insert_query)

        except (Exception, Error) as er:
            logger.error(f"Can't insert event query into database: {er}")
            return False
        else:
            logger.debug(f"Data event was successfully inserted!")
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
            logger.error(f"Can't update event query in database: {er}")
            return False
        else:
            logger.debug(f"Data event was successfully updated!")
            return True

    def get_events(self, filters: dict) -> list:
        """Gettings info about events by filters.

        Args:
            filters (dict): Filters.

        Returns:
            list: Available events.
        """
        try:
            insert_query = sql.SQL('SELECT * FROM events')
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

    def insert_user(self, data: list) -> bool:
        try:
            insert_query = sql.SQL('INSERT INTO users (user_id, username, user_role) VALUES ({})').format(
                sql.SQL(', ').join(map(sql.Literal, data)))

            with self.conn.cursor() as curs:
                curs.execute(insert_query)

        except (Exception, Error) as er:
            logger.error(f"Can't insert user query into database: {er}")
            return False
        else:
            logger.debug(f"Data user was successfully inserted!")
            return True

    def update_user(self, user_id: str, data: dict) -> bool:
        try:
            params = [sql.SQL('=').join([sql.Identifier(key), sql.Literal(value)]) for key, value in data.items()]
            insert_query = sql.SQL('UPDATE users SET {} WHERE user_id=%s').format(sql.SQL(', ').join(params))

            with self.conn.cursor() as curs:
                curs.execute(insert_query, (user_id,))

        except (Exception, Error) as er:
            logger.error(f"Can't update user query in database: {er}")
            return False
        else:
            logger.debug(f"Data user was successfully updated!")
            return True

    def get_user(self, user_id: int) -> list:
        try:
            insert_query = sql.SQL('SELECT * FROM users WHERE user_id=%s')

            user = []
            with self.conn.cursor() as curs:
                curs.execute(insert_query, (user_id,))
                user = curs.fetchone()

        except (Exception, Error) as er:
            logger.error(f"Can't get user: {er}")
            return None
        else:
            logger.debug(f"User was successfully got!")
            return user

    def get_users(self, user_type: int) -> list:
        try:
            insert_query = sql.SQL('SELECT user_id, username FROM users WHERE user_role=%s')

            users = []
            with self.conn.cursor() as curs:
                curs.execute(insert_query, (user_type,))
                users = curs.fetchall()

        except (Exception, Error) as er:
            logger.error(f"Can't get user: {er}")
            return None
        else:
            logger.debug(f"User was successfully got!")
            return users
