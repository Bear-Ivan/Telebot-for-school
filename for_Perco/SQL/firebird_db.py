import fdb
import logging
import requests
from Secret.config import admin_id, bot_spam, PATH_FBDB, LOGIN_FBDB, PASS_FBDB

logger = logging.getLogger('firebird')


class FBDB():

    def __init__(self) -> None:
        self.LOGIN = LOGIN_FBDB
        self.PWD = PASS_FBDB
        self.PATH = PATH_FBDB

    def connect(self) -> bool:
        try:
            con = fdb.connect(dsn=f'localhost:{self.PATH}', user=self.LOGIN, password=self.PWD)
            cur = con.cursor()
            self.con = con
            self.cur = cur
            return True
        except Exception as E:
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог подконектится к БД Firebird.\nException = {E}"}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=10)
            logger.error(f"Не смог подключиться. Ошибка  = {E}")
            return False

    def execute(self, sql: str) -> list:
        try:
            self.cur.execute(sql)
            result = []
            for row in self.cur.itermap():
                dict_row = {}
                for fieldDesc in self.cur.description:
                    head = str(fieldDesc[fdb.DESCRIPTION_NAME])
                    dict_row[head] = row[head]
                result.append(dict_row)
            return True, result
        except:
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог получить execute к БД Firebird."}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=10)
            return False, []

    def new_record(self, offset : int):
        if (self.connect()):
            sql = f"SELECT ID_REG, IDENTIFIER, LAST_TIMESTAMP from REG_EVENTS WHERE IDENTIFIER IS NOT NULL AND IDENTIFIER !=0 AND ID_REG > {int(offset)} ORDER BY ID_REG DESC;"
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, result
            else:
                self.close()
                return False, []
        else:
            return False, []



        return state_db, result

    def last_id(self):
        if (self.connect()):
            sql = f"SELECT FIRST 1 ID_REG from REG_EVENTS WHERE IDENTIFIER IS NOT NULL AND IDENTIFIER !=0 ORDER BY ID_REG DESC;"
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, result[0]['ID_REG']
            else:
                self.close()
                return False, []
        else:
            return False, []

    # def check(self) -> bool:
    #     try:
    #         self.cur.execute('SELECT 1 FROM RDB$DATABASE;')
    #     except Exception as E:
    #         logger.error(f"Не смог проверить. Ошибка  = {E}")
    #         self.close()
    #         if (self.connect()):
    #             self.cur.execute('SELECT 1 FROM RDB$DATABASE;')
    #         else:
    #             return False
    #
    #     if len(self.cur.fetchone()) > 0:
    #         return True
    #     else:
    #         self.close()
    #         if (self.connect()):
    #             self.cur.execute('SELECT 1 FROM RDB$DATABASE;')
    #             if len(self.cur.fetchone()) > 0:
    #                 return True
    #             else:
    #                 return False

    def close(self):
        try:
            self.cur.close()
            self.con.close()
            # print("отключился от FB")
        except:
            pass

