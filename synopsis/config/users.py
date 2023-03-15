#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import IntEnum, auto
from dataclasses import dataclass

class UserType(IntEnum):
    owner: int = auto()
    admin: int = auto()
    user: int = auto()

users = UserType