import sqlite3
import logging
import os
import requests

logger = logging.getLogger('sqlite3')
from Secret.config import admin_id, bot_spam


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class sqllite():
    def __init__(self) -> None:
        dirpath = os.path.abspath(os.path.dirname(__file__))
        self.PATH = os.path.join(dirpath, 'subscribers.sqllitedb')

    def connect(self) -> bool:
        try:
            con = sqlite3.connect(self.PATH)
            con.row_factory = dict_factory
            cur = con.cursor()
            self.con = con
            self.cur = cur
            return True

        except Exception as E:
            logger.error(f"Не смог подключиться. Ошибка  = {E}")
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог подконектится к БД SQLlite.\nException = {E}"}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
            return False

    def execute(self, sql: str, commit: bool = False):
        if commit:
            try:
                self.cur.execute(sql)
                self.con.commit()
                return True, []
            except:
                params_spambot = {'chat_id': admin_id,
                                  'text': f"Не смог execute к БД SQLlite."}
                requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
                return False, []
        else:
            try:
                return True, self.cur.execute(sql).fetchall()
            except:
                params_spambot = {'chat_id': admin_id,
                                  'text': f"Не смог execute к БД SQLlite."}
                requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
                return False, []

    def close(self):
        try:
            self.cur.close()
            self.con.close()
            # print('соединение закрыл с БД')
        except:
            pass

    def check(self) -> bool:
        try:
            self.cur.execute('SELECT 1;')
        except Exception as E:
            logger.error(f"Не смог проверить. Ошибка  = {E}")
            self.close()
            if (self.connect()):
                self.cur.execute('SELECT 1;')
            else:
                return False

        if len(self.cur.fetchone()) > 0:
            return True
        else:
            self.close()
            if (self.connect()):
                self.cur.execute('SELECT 1;')
                if len(self.cur.fetchone()) > 0:
                    return True
                else:
                    return False

    def check_table(self):
        _, results = self.execute("SELECT name FROM sqlite_master;")
        x = 0
        y = 0
        for result in results:
            if result['name'] == 'subscribers':
                x += 1
            if result['name'] == 'system_time':
                # для своей системной таблицы, может пригодится
                y += 1
        if x == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы subscribers!!!!!!!!!!
            st, _ = self.execute(
                "CREATE TABLE subscribers (id INTEGER PRIMARY KEY, card_id numeric,fio_child text, class text, relationship text, fio_relationship text, telegramid_relationship numeric, telegram_fullname text, data_zapisi datetime, need_send integer);",
                commit=True)
            if st:
                print("создал таблицу subscribers")
        if y == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы system_time!!!!!!!!!!
            st, _ = self.execute("CREATE TABLE system_time (data_reset datetime,bool_flag integer);", commit=True)
            if st:
                print("создал таблицу system_time")
            st, _ = self.execute("INSERT INTO system_time (bool_flag) values(0);", commit=True)
            if st:
                print("Вставил пустую строку при инициализации в таблицу system_time")

    def get_give(self, sql: str, commit: bool = False):
        if (self.connect()):
            state, result = self.execute(sql, commit)
            self.close()
            return state, result
        else:
            return False, []
