from Telegram.loader import bot, storage
import asyncio
import logging
import os
from SQL.sqllite_db import sqllite
from SQL.firebird_db import FBDB
from Secret.config import sleep_FBDB, admin_id

# add filemode="w" to overwrite
logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(module)s :%(name)s : %(message)s')
logging.getLogger('urllib3').setLevel('CRITICAL')
loop = asyncio.get_event_loop()


async def shutdown(dp):
    print('on_shutdown')
    await bot.close()
    await storage.close()


async def req_SKUD():
    await asyncio.sleep(3)
    global last_id_FBDB

    while True:
        # print("круг опроса начал")
        # print(f"last_id_FBDB = {last_id_FBDB}")
        state_NR, result_NR = FBDB().new_record(offset=last_id_FBDB)
        if state_NR:
            if len(result_NR) > 0:
                last_id_FBDB = result_NR[0]["ID_REG"]

                list_cardid = [f"{int(k['IDENTIFIER'])}" for k in result_NR]
                # получаем список кому нужно отправлять записи о приходе в школу
                status_sqllit, result_sqllite = sqllite().get_give(
                    f"SELECT telegramid_relationship, fio_child, class, card_id from subscribers  WHERE card_id in ({', '.join(list_cardid)}) and need_send=1;")
                if status_sqllit:
                    if len(result_sqllite) > 0:
                        # есть записи для оповещения
                        for parent in result_sqllite:
                            for new_zapis in result_NR:
                                cardid = int(new_zapis["IDENTIFIER"])
                                time_zapis = new_zapis["LAST_TIMESTAMP"]
                                if int(parent['card_id']) == cardid:
                                    text_to_par = f"{parent['fio_child']}, {parent['class']} прошёл(ла) через турникет в {time_zapis.strftime('%d/%m/%Y %H:%M:%S')}"
                                    await bot.send_message(chat_id=parent['telegramid_relationship'],
                                                           text=text_to_par)
                else:
                    logger.error(f"Не смог получить данные кому рассылать из SQLlite, при опросе по кругу")
        else:
            logger.error(f"Не смог подключиться к БД firebird при опросе по кругу")
        # print("круг опроса закончил, сон")
        await asyncio.sleep(sleep_FBDB)


if __name__ == '__main__':
    # абсолютный путь к папке
    path_base = os.path.abspath(os.path.dirname(__file__))

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
    status_FBDB, last_id_FBDB = FBDB().last_id()
    if status_FBDB:
        print("Получил last_id_FBDB успешно")
        print("Подключил req_SKUD() в асинхронность")
        # Добавление таска по опросу базы firebird
        loop.create_task(req_SKUD())


    executor.start_polling(dp, loop=loop, on_startup=send_to_Admin, on_shutdown=shutdown)
