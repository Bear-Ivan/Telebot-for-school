from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import review
from SQL.sqllite_db import sqllite
from Secret.config import admin_id, bot_spam
import requests


@dp.message_handler(Command("reviews"), state=None)
async def enter_test(message: types.Message):
    await message.answer('Введите сообщение, что хотите переслать администратору.\nДля выхода в главное меню нажмите /cancel')
    await review.Q1.set()


@dp.message_handler(state=review.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')

    db = sqllite()
    status_db, res = db.get_give(
        f"SELECT card_id, class,relationship,fio_relationship from subscribers  WHERE telegramid_relationship ={int(message.from_user.id)} and need_send = 1")
    text_card = ''
    if status_db:
        if len(res) > 0:
            for card in res:
                text_card += f"Карта:{card['card_id']}, Класс:{card['class']}, Для ребенка:{card['relationship']}, ФИО родителя:{card['fio_relationship']}\n"

    review_full = f'От: chatid = {message.from_user.id}\nФИО телеграмм = {message.from_user.full_name}\nИнфо по пользователю:\n{text_card}\nСообщение:\n{answer}'
    params_spambot = {'chat_id': admin_id, 'text': review_full}
    response_spam = requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
    if response_spam.status_code == 200:
        await message.reply(f'Ваше сообщение успешно отправлено администратору.')
    else:
        await message.reply(f"Ой, что-то пошло не так. Попробуйте позже.")
    # освобождение памяти
    await state.finish()
