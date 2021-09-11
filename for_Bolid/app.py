from Telegram.loader import bot, storage
import asyncio
import logging
import os
from SQL.sqllite_db import sqllite
from SQL.sqlserver_db import SQLServer
from Secret.config import sleep_circle, admin_id, bot_spam, update_pmark
from datetime import datetime, timedelta
import requests
import ntplib

# add filemode="w" to overwrite
logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(module)s :%(name)s : %(message)s')
logging.getLogger('urllib3').setLevel('CRITICAL')
logger = logging.getLogger('app')
loop = asyncio.get_event_loop()

dic_par4 = {1: 'Вход',
            2: 'Выход'}


async def shutdown(dp):
    print('on_shutdown')
    await bot.close()
    await storage.close()


def convert(code):
    strb = ""
    dic_code = {
        "fe01": "00",
        "fe02": "fe",
        "fe03": "20",
        "fe04": "5c",
        "fe05": "0a"
    }

    for a in code:
        chislo = hex(a).split('x')[-1]
        if len(chislo) == 1:
            strb += "0" + hex(a).split('x')[-1]
        else:
            strb += hex(a).split('x')[-1]

    for k, v in dic_code.items():
        strb = strb.replace(k, v)

    if len(strb) == 18:
        return strb[4:10]
    if len(strb) > 18:
        logger.error(f"Добавь что-то новое в dic_code")
        params_spambot = {'chat_id': admin_id,
                          'text': f"Добавь что-то новое в dic_code. code = {code}, после преобразования = {strb}"}
        try:
            requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
        except:
            pass
        return None
    else:
        return None


def win_set_time():
    try:
        import win32api
        c = ntplib.NTPClient()
        response = c.request('time.windows.com')
        # время с NTP сервера
        cur_time = datetime.utcfromtimestamp(response.tx_time)
        # время с NTP сервера с тайм зоной
        # td = cur_time + timedelta(hours=7)
        win32api.SetSystemTime(cur_time.year, cur_time.month, cur_time.isocalendar()[2], cur_time.day, cur_time.hour,
                               cur_time.minute, cur_time.second, cur_time.microsecond // 1000)
    except Exception as e:
        logger.error(f"Не удалось подправить время на ПК. Ошибка = {e}")


def pmark_code():
    state_codep, result_codep = SQLServer().get_pmarkcode()
    # sql = "INSERT INTO pmark_code (codep,owner,ownername) VALUES(%s,%s,%s)"
    data = []
    if state_codep:
        for mes in result_codep:
            des_codep = convert(mes['codep'])
            if des_codep:
                data.append((des_codep, mes['Owner'], mes['OwnerName']))
        if len(data) > 0:
            state_pmark = sqllite().execute_many_pmark(data)
            if state_pmark:
                logger.info("Обновил список pmark успешно")
    else:
        logger.error(f"SQL server не выдал таблицу pmark")


async def req_SKUD():
    # from Secret.config import lasttime
    await asyncio.sleep(3)
    global last_timesqlserv

    while True:
        # print("круг опроса начал")
        logger.info(f"круг опроса начал")

        # обновление pMark новыми кодами
        state, res = sqllite().get_give(sql="SELECT datatime_pmark_time, bool_flag from pmark_time")
        if state:
            if res[0]['bool_flag'] == 0:
                pmark_code()
                win_set_time()
            else:
                time_now = datetime.now()
                datatime_pmark_time = datetime.strptime(res[0]['datatime_pmark_time'], '%d/%m/%Y %H:%M:%S')
                diff_time = (time_now - datatime_pmark_time).seconds
                # print(diff_time)
                if diff_time > update_pmark:
                    pmark_code()
                    win_set_time()
        # конец обновления pMark новыми кодами

        print(f"last_timesqlserv = {last_timesqlserv}")
        state_NR, result_NR = SQLServer().new_record(offset=last_timesqlserv)
        if state_NR:
            if len(result_NR) > 0:
                last_timesqlserv = result_NR[-1]["TimeVal"]
                # lasttime = last_timesqlserv

                list_HozOrgan = [f"{int(k['HozOrgan'])}" for k in result_NR]
                # получаем список кому нужно отправлять записи о приходе в школу
                status_sqllit, result_sqllite = sqllite().get_give(
                    f"SELECT sub.telegramid_relationship, sub.fio_child, sub.class, pmark.owner from subscribers as sub left join pmark_code as pmark on sub.card_uid_hex = pmark.codep WHERE pmark.owner in ({', '.join(list_HozOrgan)}) and need_send=1;")
                if status_sqllit:
                    if len(result_sqllite) > 0:
                        # есть записи для оповещения
                        for parent in result_sqllite:
                            for new_zapis in result_NR:
                                owner = int(new_zapis["HozOrgan"])
                                time_zapis = new_zapis["TimeVal"].strftime('%d/%m/%Y %H:%M:%S')
                                if int(parent['owner']) == owner:
                                    text_to_par = f"{parent['fio_child']}, {parent['class']} {dic_par4[new_zapis['Par4']]} {time_zapis}"
                                    #  отправка сообщения, пробует 3 раза, если не получилось то дропит
                                    count = 0
                                    while True:
                                        try:
                                            count += 1
                                            await bot.send_message(chat_id=parent['telegramid_relationship'],
                                                                   text=text_to_par)
                                            logger.info(f"Сообщение успешно отправил. {text_to_par}")
                                            break
                                        except:
                                            await asyncio.sleep(10)
                                            if count == 3:
                                                logger.error(f"Не смог отправить сообщение. {text_to_par}")
                                                break
                else:
                    logger.error(f"Не смог получить данные кому рассылать из SQLlite, при опросе по кругу")
        else:
            logger.error(f"Не смог подключиться к БД firebird при опросе по кругу")

        # print("круг опроса закончил, сон")
        logger.info(f"круг опроса закончил, сон")
        await asyncio.sleep(sleep_circle)


if __name__ == '__main__':
    # абсолютный путь к папке
    # path_base = os.path.abspath(os.path.dirname(__file__))

    from aiogram import executor
    from Telegram.handlers import dp, send_to_Admin

    # проверка создана ли база sqllite
    db_sqllite = sqllite()
    if (db_sqllite.connect()):
        db_sqllite.check_table()
        db_sqllite.close()
    else:
        print("Проверь ДБ sqllite, не смог подключиться при первом обращении.")
        logger.error(f"Проверь ДБ sqllite, не смог подключиться при первом обращении.")

    # получение крайнего lastid для FB
    status_sqlserv, last_timesqlserv = SQLServer().last_time()
    if status_sqlserv:
        print("Получил last_timesqlserv успешно" + str(last_timesqlserv))
        print("Подключил req_SKUD() в асинхронность")
        # Добавление таска по опросу базы SQLserver
        loop.create_task(req_SKUD())

    executor.start_polling(dp, loop=loop, on_startup=send_to_Admin, on_shutdown=shutdown)
