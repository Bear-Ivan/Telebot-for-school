from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import check_card
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


@dp.message_handler(Command("check"), state=None)
async def enter_test(message: types.Message):
    await message.answer(f'Введите номер карты, по которой хотите посмотреть кто подписан. Например 0001111111. Или кликните по карте в следующем сообщении.\nЕсли передумали жми /cancel')
    db = sqllite()
    status_db, res = db.get_give(
        f"SELECT card_id, class from subscribers  WHERE telegramid_relationship ={int(message.from_user.id)} and need_send = 1")
    if status_db:
        if len(res) > 0:
            text_card= ''
            for card in res:
                text_card += f"/{card['card_id']} {card['class']} класс\n"
            await message.answer(f'Вы подписаны на следующие карты:\n{text_card}Нажмите на карту из списка, для получения подробной информации.')
        else:
            await message.answer(f'Вы пока не подписаны ни на одну карту.')
    else:
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    await check_card.Q1.set()


@dp.message_handler(state=check_card.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    cardid = check_number_Card(answer)

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif cardid:
        db = sqllite()
        status_db, res = db.get_give(f"SELECT telegram_fullname,fio_relationship from subscribers  WHERE card_id ={int(cardid)} and need_send = 1")
        if status_db:
            if len(res) > 0:
                text_people = f'Всего на карту подписано {len(res)} человека:\n'
                for people in res:
                    text_people += f"ФИО из telegram: <b>{people['telegram_fullname']}</b>, ФИО из авторизации: <b>{people['fio_relationship']}</b>\n"
            else:
                text_people = f"Пока на данную карту никто не подписан."
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
        # продолжаем
        await message.reply(text_people)
    else:
        return await message.reply('Нужно вввести 10 цифр попробуй еще раз. Если передумали жми /cancel')

    # освобождение памяти
    await state.finish()