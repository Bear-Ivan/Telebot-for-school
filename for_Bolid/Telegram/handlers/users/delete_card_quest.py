from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import delete_card
from SQL.sqllite_db import sqllite
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


@dp.message_handler(Command("delete"), state=None)
async def enter_test(message: types.Message):
    db = sqllite()
    status_db, res = db.get_give(
        f"SELECT card_id, class, fio_child from subscribers  WHERE telegramid_relationship ={int(message.from_user.id)} and need_send = 1")
    if status_db:
        if len(res) > 0:
            text_card = ''
            for card in res:
                text_card += f"/{card['card_id']} ФИО:<b>{card['fio_child']}</b> класс:<b>{card['class']}</b>\n"
            await message.answer(
                f'Вы подписаны на следующие карты:\n{text_card}\nНажмите на карту из списка, чтобы отписаться.\nДля выхода в главное меню нажмите /cancel')
        else:
            return await message.reply(f'Вы пока не подписаны ни на одну карту. Вышел в главное меню.')
    else:
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    await delete_card.Q1.set()


@dp.message_handler(state=delete_card.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    cardid = check_number_Card(answer)

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif cardid:
        db = sqllite()
        status_db, _ = db.get_give(
            f"UPDATE subscribers SET need_send = 0 WHERE telegramid_relationship = {int(message.from_user.id)} and card_id ={int(cardid)};",
            commit=True)
        if status_db:
            await message.reply("Вы успешно отписались от карты.")
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    else:
        return await message.reply('Нужно вввести UID карты, попробуй еще раз.\nДля выхода в главное меню нажмите /cancel')

    # освобождение памяти
    await state.finish()
