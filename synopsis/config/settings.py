#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from environs import Env
from dataclasses import dataclass

@dataclass
class Database:
    name    : str
    user    : str
    password: str
    host    : str
    port    : int

@dataclass
class Bots:
    token  : str
    version: str

@dataclass
class Settings:
    bots: Bots
    db  : Database

def get_settings():
    env = Env()
    env.read_env()

    with open("bot_settings.json", "r") as f:
        settings_json = json.load(f)

    return Settings(
        bots=Bots(
            token   = env.str('BOT_TOKEN'),
            version = settings_json.get('bot_version', 'v1.0.0')
        ),
        db=Database(
            name     = env.str('DB_NAME'),
            user     = env.str('PG_USER'),
            password = env.str('PG_PASSWORD'),
            host     = env.str('PG_HOST'),
            port     = env.int('PG_PORT')
        )
    )

settings = get_settings()