#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

with open("bot_settings.json", "r") as f:
    settings_json = json.load(f)

class BotAuth:
    """Данные авторизации бота.
    """
    BOT_VERSION = settings_json.get('bot_version', 'v1.0.0')
    BOT_TOKEN   = os.getenv('BOT_TOKEN')

class Database:
    """Данные авторизации базы данных PostgreSql.
    """
    DB_NAME     = os.getenv('DB_NAME')
    PG_USER     = os.getenv('PG_USER')
    PG_PASSWORD = os.getenv('PG_PASSWORD')
    PG_HOST     = os.getenv('PG_HOST')
    PG_PORT     = int(os.getenv('PG_PORT'))