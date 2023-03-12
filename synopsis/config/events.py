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
    sport : int = auto()

class Time(IntEnum):
    before_12 : int = auto()

class Date(IntEnum):
    today     : int = auto()
    tomorrow  : int = auto()
    next_week : int = auto()

class Duration(IntEnum):
    min_30 : int = auto()

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