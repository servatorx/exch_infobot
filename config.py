# -*- coding: utf-8 -*-

from enum import Enum

token = '' # Вставить сюда токен бота
db_file = "database.vdb"


class States(Enum):

    S_START = "0"  # Начало нового диалога
    S_ENTER_TYPE = "1"
    S_ENTER_CODE = "2"
    S_ENTER_DAY = "3"
    S_ENTER_MONTH = "4"
    S_ENTER_YEAR = "5"
    S_ENTER_HIST = "6"
