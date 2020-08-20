
# -*- coding: utf-8 -*-

from vedis import Vedis
import config


# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id].decode() 
        except KeyError:  # Если такого ключа почему-то не оказалось
            return config.States.S_START.value  

# Пытаемся узнать из базы «состояние» пользователя
def del_state(field):
    with Vedis(config.db_file) as db:
        try:
            del db[field]
            return True 
        except:  
            return False  


def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:

            return False


def set_property(user_id, value, pr_name):
    with Vedis(config.db_file) as db:
        try:
            db[str(user_id)+pr_name] = value
            return True
        except:

            return False
def get_property(user_id, pr_name):
    with Vedis(config.db_file) as db:
        try:
            return db[str(user_id)+pr_name].decode() 
        except KeyError:  
            return config.States.S_START.value  

def set_curr_hist(cur_name, date, value):
    with Vedis(config.db_file) as db:
        cur_ind = str(cur_name) + str(date)
        try:
            db[str(cur_ind)] = value
            return True
        except:

            return False
def get_curr_hist(cur_name, date):
    with Vedis(config.db_file) as db:
        cur_ind = str(cur_name) + str(date)
        try:
            return db[cur_ind].decode() 
        except KeyError:  
            return config.States.S_START.value