from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import reset
from SQL.sqllite_db import sqllite
from Secret.config import admin_id, bot_spam
from datetime import datetime


@dp.message_handler(Command("reset"), state=None)
async def enter_test(message: types.Message):
    if (message.from_user.id == admin_id):
        await message.answer(
            'Вы уверены, что хотите отписать всех пользователей от рассылки и разослать всем уведомления об этом?\nНапиши да или нет.\nДля выхода в главное меню нажмите /cancel')
        await reset.Q1.set()


@dp.message_handler(state=reset.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    if (message.from_user.id == admin_id):
        answer = message.text
        if answer == '/cancel':
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')

        if answer.lower() == 'нет':
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')

        if answer.lower() == 'да':
            db = sqllite()
            if db.connect():
                # Всем сообщение о начале нового учебного года.
                status_db, res = db.execute(
                    "SELECT DISTINCT telegramid_relationship from subscribers WHERE need_send=1;")
                if status_db:
                    text_mes = f"Доброго времени суток.\nВпереди новый учебный год.\n" \
                               f"Все подписки сброшены. Если ваш ребенок продолжает учиться в лицее, " \
                               f"прошу актуализировать данные по подписке. Нажмите на /prolongation и пройдите опрос.\n" \
                               f"Кнопка /prolongation будет активна 3 дня с момента написания сообщения, дальнейшая подписка через стандартную кнопку /add."

                    er = ""
                    for mes in res:
                        try:
                            await bot.send_message(chat_id=int(mes['telegramid_relationship']), text=text_mes)
                        except:
                            er += f"Не смог отправить для chatid = {int(mes['telegramid_relationship'])}\n"

                    # ответ админу
                    if er:
                        await message.answer(f"Собщение всем подписчикам разослал, кроме:\n {er}")
                    else:
                        await message.answer("Собщение всем подписчикам разослал успешно.")
                else:
                    return await message.reply('Ой, что-то не так c нашей БД на этапе execute. Попробуйте позже.')
                # чистка DB
                status_db, _ = db.execute("DELETE FROM subscribers WHERE need_send = 0;", commit=True)
                if status_db:
                    await message.answer("Почистил DB успешно, от старых подписчиков")
                else:
                    await message.answer("Не удалось почистить DB, от старых подписчиков")

                # отписка всех подписчиков от карт
                status_db, _ = db.execute("UPDATE subscribers SET need_send = 0 WHERE need_send = 1;", commit=True)
                if status_db:
                    await message.answer("Успешно отписал всех подписчиков от карт")
                else:
                    await message.answer("Не удалось отписал всех подписчиков от карт")

                # постановка системного времени в БД о том что записи сброшены
                status_db, _ = db.execute(
                    f"UPDATE system_time SET bool_flag = 1, data_reset = '{str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}';",
                    commit=True)
                if status_db:
                    await message.answer("Системное время установил, при команде ресет")
                else:
                    await message.answer("Не удалось установить системное время, при команде ресет")
                # закрытие DB
                db.close()
            else:
                return await message.reply('Ой, что-то не так c нашей БД на этапе connect. Попробуйте позже.')
        else:
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')

        # освобождение памяти
        await state.finish()
