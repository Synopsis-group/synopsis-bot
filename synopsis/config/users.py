#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from environs import Env
from dataclasses import dataclass

@dataclass
class Users:
    owners: list

def get_users():
    env = Env()
    env.read_env()

    return Users(
        owners=env.list('OWNERS_ID', delimiter=',', subcast=int)
    )

users = get_users()