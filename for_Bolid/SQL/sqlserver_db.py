import pyodbc
import logging
import requests
from Secret.config import admin_id, bot_spam, server, database, username, password
from datetime import datetime

logger = logging.getLogger('SQL_server_2012')


class SQLServer():

    def __init__(self) -> None:
        self.server = server
        self.username = username
        self.password = password
        self.database = database

    def connect(self) -> bool:
        try:
            con = pyodbc.connect(Trusted_Connection='yes', driver='{SQL Server}', server=self.server,
                                 database=self.database, UID=self.username, PWD=self.password)

            # для дебага
            # con = pyodbc.connect(
            #     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
            cur = con.cursor()
            self.con = con
            self.cur = cur
            return True
        except Exception as E:
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог подконектится к БД SQLserver.\nException = {E}"}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=10)
            logger.error(f"Не смог подключиться. Ошибка  = {E}")
            return False

    def execute(self, sql: str) -> list:
        try:
            self.cur.execute(sql)
            columns = [column[0] for column in self.cur.description]
            result = []
            for row in self.cur.fetchall():
                result.append(dict(zip(columns, row)))
            return True, result
        except Exception as E:
            params_spambot = {'chat_id': admin_id,
                              'text': f"Не смог получить execute к БД Firebird."}
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=10)
            logger.error(f"Не смог execute. Ошибка  = {E}")
            return False, []

    def new_record(self, offset: datetime):
        if (self.connect()):
            sql = f"""SELECT TimeVal, HozOrgan, Par4 from [dbo].[pLogData] WHERE Par4 in (1,2) and Par3 in (1,2,3,4) and [dbo].[pLogData].[HozOrgan] IS NOT NULL AND [dbo].[pLogData].[HozOrgan] !=0 AND [dbo].[pLogData].[TimeVal] > CONVERT (datetime,'{offset.strftime("%Y-%m-%d %H:%M:%S")}', 21) ORDER BY TimeVal ASC;"""
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, result
            else:
                self.close()
                return False, []
        else:
            return False, []

    def last_time(self):
        if (self.connect()):
            sql = f"SELECT TOP(1) TimeVal from [dbo].[pLogData] ORDER BY TimeVal DESC;"
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, result[0]['TimeVal']
            else:
                self.close()
                return False, []
        else:
            return False, []

    def get_history(self, HozOrgan: int):
        if (self.connect()):
            sql = f"""SELECT TOP(14) TimeVal, Par4 from [dbo].[pLogData] WHERE Par4 in (1,2) and Par3 in (1,2,3,4)  AND [dbo].[pLogData].[HozOrgan] = {HozOrgan} ORDER BY TimeVal DESC;"""
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, list(reversed(result))
            else:
                self.close()
                return False, []
        else:
            return False, []

    def get_pmarkcode(self):
        if (self.connect()):
            sql = f"select cast(codep as binary varying) as codep, Owner, OwnerName  from [dbo].[pMark]"
            state_db, result = self.execute(sql)
            if state_db:
                self.close()
                return True, result
            else:
                self.close()
                return False, []
        else:
            return False, []

    def close(self):
        try:
            self.cur.close()
            self.con.close()
            # print("отключился от sqlserver")
        except:
            pass