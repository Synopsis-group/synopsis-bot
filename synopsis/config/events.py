#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import IntEnum, auto
from dataclasses import dataclass

class Status(IntEnum):
    new      : int = auto()
    changed  : int = auto()
    cancled  : int = auto()
    finished : int = auto()

class Type(IntEnum):
    sport     : int = auto()
    education : int = auto()
    culture   : int = auto()

class Time(IntEnum):
    before_12     : int = auto()
    between_12_16 : int = auto()
    between_16_19 : int = auto()
    after_19      : int = auto()

class Date(IntEnum):
    today     : int = auto()
    tomorrow  : int = auto()
    next_week : int = auto()

class Duration(IntEnum):
    min_30    : int = auto()
    hour_1    : int = auto()
    hour_1_30 : int = auto()
    hour_2    : int = auto()
    hour_3    : int = auto()
    more_3    : int = auto()

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