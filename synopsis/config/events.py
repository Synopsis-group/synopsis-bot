#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, IntEnum, auto
from dataclasses import dataclass

class Status(IntEnum):
    new      = auto()
    changed  = auto()
    cancled  = auto()
    finished = auto()

class Type(Enum):
    sport      = (1, "Спорт")
    education  = (2, "Образование")
    culture    = (3, "Культура")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class Time(Enum):
    before_12 = (1, "До 12")
    between_12_16 = (2, "С 12 до 16")
    between_16_19 = (3, "С 16 до 19")
    after_19      = (4, "После 19")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class Date(Enum):
    today     = (1, "Сегодня")
    tomorrow  = (2, "Завтра")
    next_week = (3, "Ближайшая неделя")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class Duration(Enum):
    min_30    = (1, "~30 мин")
    hour_1    = (2, "~1 час")
    hour_1_30 = (3, "~1 час 30 мин")
    hour_2    = (4, "~2 часа")
    hour_3    = (5, "~3 часа")
    more_3    = (6, "Более 3 часов")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

@dataclass
class Event:
    status  : Status
    type    : Type
    time    : Time
    date    : Date
    duration: Duration

def get_events():
    return Event(
        status   = Status,
        type     = Type,
        time     = Time,
        date     = Date,
        duration = Duration
    )

events = get_events()