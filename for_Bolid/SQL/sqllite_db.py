import sqlite3
import logging
import os
import requests
from datetime import datetime

from Secret.config import admin_id, bot_spam

logger = logging.getLogger('sqlite3')


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

    def execute_many_pmark(self, data: list):
        sql = "INSERT INTO pmark_code (codep,owner,ownername) VALUES(?,?,?)"
        try:
            if (self.connect()):
                res, _ = self.execute(sql="DELETE FROM pmark_code;", commit=True)
                if res:
                    logger.info("Успешно очистил таблицу pmark_code")
                    datas = []
                    x = 0
                    for dat in data:
                        datas.append(dat)
                        x += 1
                        if (x % 500) == 0:
                            self.cur.executemany(sql, datas)
                            self.con.commit()
                            datas = []
                            logger.debug("execute_many отправил 500 штук")

                    if len(datas) > 0:
                        self.cur.executemany(sql, datas)
                        self.con.commit()
                        logger.debug(f"execute_many отправил крайнии {len(datas)} штук")
                    logger.info("Успешно заполнил таблицу pmark_code новыми кодами")

                    # обновление времени в sqllite
                    status_db, _ = self.execute(
                        f"UPDATE pmark_time SET bool_flag = 1, datatime_pmark_time = '{str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}';",
                        commit=True)
                    if status_db:
                        logger.info("Успешно обновил время в pmark_time")
                        self.close()
                        return True
                self.close()
            else:
                params_spambot = {'chat_id': admin_id,
                                  'text': f"Не смог подключиться к execute_many_pmark SQLlite. Таблица не обновлена."}
                requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
                logger.error(f"Не смог подключиться к execute_many_pmark SQLlite. Таблица не обновлена.")
                return False
        except Exception as E:
            logger.error(f"Не смог execute_many_pmark. Ошибка = {E}")
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог execute_many_pmark. Ошибка = {E}"}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
            self.close()
            return False

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
        z = 0
        w = 0

        for result in results:
            if result['name'] == 'subscribers':
                x += 1
            if result['name'] == 'system_time':
                # для своей системной таблицы, может пригодится
                y += 1
            if result['name'] == 'pmark_code':
                # для своей системной таблицы, может пригодится
                z += 1
            if result['name'] == 'pmark_time':
                # для своей системной таблицы, может пригодится
                w += 1
        if x == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы subscribers!!!!!!!!!!
            st, _ = self.execute(
                "CREATE TABLE subscribers (card_id bigint,fio_child varchar[100], class varchar[5], relationship  varchar[50], fio_relationship  varchar[100], telegramid_relationship bigint, telegram_fullname text, data_zapisi datetime, need_send integer, card_uid_hex varchar[10]);",
                commit=True)
            if st:
                logger.info(f"создал таблицу subscribers")

        if y == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы system_time!!!!!!!!!!
            st, _ = self.execute("CREATE TABLE system_time (data_reset datetime,bool_flag integer);", commit=True)
            if st:
                logger.info(f"создал таблицу system_time")
                st, _ = self.execute("INSERT INTO system_time (bool_flag) values(0);", commit=True)
                if st:
                    logger.info(f"Вставил пустую строку при инициализации в таблицу system_time")

        if z == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы subscribers!!!!!!!!!!
            st, _ = self.execute(
                "CREATE TABLE pmark_code (codep varchar[10], owner bigint, ownername varchar[30]);",
                commit=True)
            if st:
                logger.info(f"создал таблицу pmark_code")

        if w == 0:
            # !!!!!!!!!!!!!SQL Запрос на содание таблицы subscribers!!!!!!!!!!
            st, _ = self.execute("CREATE TABLE pmark_time (datatime_pmark_time datetime, bool_flag integer);",
                                 commit=True)
            if st:
                logger.info(f"создал таблицу pmark_time")
                st, _ = self.execute("INSERT INTO pmark_time (bool_flag) values(0);", commit=True)
                if st:
                    logger.info(f"Вставил пустую строку при инициализации в таблицу pmark_time")

    def get_give(self, sql: str, commit: bool = False):
        if (self.connect()):
            state, result = self.execute(sql, commit)
            self.close()
            return state, result
        else:
            return False, []
