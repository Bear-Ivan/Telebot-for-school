from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import prolongation
from SQL.sqllite_db import sqllite
from Secret.config import admin_id, reset_podpiska
from datetime import datetime
import re


def check_number_Card(text: str):
    try:
        card_id = re.search(r'\d+', text).group()
    except:
        return False
    number = 0
    for simvol in card_id:
        if simvol == '0':
            number += 1
        else:
            break
    if ((len(card_id[number:]) > 0) and (len(card_id[number:]) < 11)):
        return int(card_id[number:])
    else:
        False


@dp.message_handler(Command("prolongation"), state=None)
async def enter_test(message: types.Message):
    db = sqllite()
    if db.connect():
        status_db, res = db.execute("SELECT bool_flag, data_reset from system_time;")
        if status_db:
            if res[0]['bool_flag'] == 1:
                reset_time = datetime.strptime(res[0]['data_reset'], '%d/%m/%Y %H:%M:%S')
                time_now = datetime.now()
                if time_now > reset_time:
                    diff_time = (time_now - reset_time).days
                    # diff_time = (time_now - reset_time).seconds
                    if diff_time < (reset_podpiska + 1):
                        # прошло не более 3 дней
                        status_db, res = db.execute(
                            f"SELECT card_id,fio_child, class from subscribers WHERE telegramid_relationship={int(message.from_user.id)} and need_send=0;")
                        db.close()
                        if status_db:
                            if len(res) > 0:
                                text_card = 'Выберите карту для продления подписки:\n'
                                for r in res:
                                    text_card += f"/{r['card_id']} ФИО:<b>{r['fio_child']}</b> класс:<b>{r['class']}</b>\n"
                                text_card += "Если передумали жми /cancel"
                                await message.answer(text_card)
                                await prolongation.Q1.set()
                            else:
                                return await message.reply(f'Вы не были подписаны ни на одну карту.')
                    else:
                        db.close()
                        return await message.reply(
                            f"Прошло более 3 дней с момента сброса подписок.\nДля подписки на карту воспользуйтесь полной формой /add")
        else:
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    else:
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')


@dp.message_handler(state=prolongation.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    cardid = check_number_Card(answer)

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif cardid:
        # продолжаем
        await state.update_data(answer1=cardid)
    else:
        return await message.reply('Если передумали жми /cancel')

    # следующий вопрос
    await message.answer("Введите класс в котором учится ребенок. Например 1Д\nЕсли передумали жми /cancel")
    await prolongation.next()


@dp.message_handler(state=prolongation.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню')
    try:
        class_child = re.search(r'\d{1,2}[а-яА-ЯёЁ]', answer).group()
        answer2 = class_child.upper()
    except:
        return await message.reply(
            'Нужно ввести номер и букву класса ребенка(на русском языке). Если передумали жми /cancel')

    # Достаем переменные
    data = await state.get_data()
    answer1 = data.get("answer1")

    db = sqllite()
    if db.connect():
        status_db, res = db.execute(
            f"UPDATE subscribers SET need_send = 1, class='{str(answer2)}', data_zapisi = '{str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}' WHERE need_send = 0 and telegramid_relationship={int(message.from_user.id)} and card_id={int(answer1)};",
            commit=True)
        if status_db:
            status_db, res = db.execute(
                f"SELECT card_id, fio_child, class, relationship, fio_relationship from subscribers WHERE telegramid_relationship={int(message.from_user.id)} and card_id ={int(answer1)};")
            if status_db:
                text_answer = ''
                for r in res:
                    text_answer += f"Карта {r['card_id']} добавлена для отслеживания.\n" \
                                   f"Ваши данные:\n" \
                                   f"Номер карты {r['card_id']}\n" \
                                   f"ФИО ребенка {r['fio_child']}\n" \
                                   f"Класс {r['class']}\n" \
                                   f"Вы для ребенка {r['relationship']}\n" \
                                   f"Ваше ФИО {r['fio_relationship']}\n"
                await message.answer(text_answer)
            else:
                await state.reset_state()
                return await message.reply(
                    f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
        # закрытие db если был к ней коннект
        db.close()
    else:
        await state.reset_state()
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')

    # освобождение памяти
    await state.finish()
