from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import history_card
from SQL.sqllite_db import sqllite
from SQL.sqlserver_db import SQLServer
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


dic_par4 = {1: 'Вход',
            2: 'Выход'}


@dp.message_handler(Command("history"), state=None)
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
                f'Вы подписаны на следующие карты:\n{text_card}\nНажмите на карту из списка, чтобы посмотреть историю проходов.\nДля выхода в главное меню нажмите /cancel')
        else:
            return await message.reply(
                f'Вы пока не подписаны ни на одну карту. Для просмотра истории посещений нужно быть подписанным на карты.\nВышел в главное меню.')
    else:
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    await history_card.Q1.set()


@dp.message_handler(state=history_card.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    cardid = check_number_Card(answer)

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif cardid:
        db = sqllite()
        status_db, res_owner = db.get_give(
            f"SELECT pmark.owner from subscribers as sub left join pmark_code as pmark on sub.card_uid_hex = pmark.codep where sub.card_id ={int(cardid)} and sub.telegramid_relationship = {int(message.from_user.id)};")
        if status_db:
            if len(res_owner) == 1:
                # получаю данные из SQLserv
                st_serv, res_serv = SQLServer().get_history(HozOrgan=res_owner[0]['owner'])
                if st_serv:
                    if len(res_serv) > 0:
                        text_answ = "История проходов через турникет:\n"
                        for prohod in res_serv:
                            text_answ += f"{prohod['TimeVal'].strftime('%d/%m/%Y %H:%M:%S')}  {dic_par4[prohod['Par4']]}\n"
                    else:
                        text_answ = f"История по карте {cardid} пуста.\nПока не было записано ни одного прохода через турникет."
                    # отправка ответа
                    await message.answer(text_answ)
            else:
                await state.reset_state()
                return await message.reply(
                    f'Вашей карты нет в БД. Попробуйте позже или обратитесь к администратору системы.\nВышел в главное меню.')
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    else:
        return await message.reply(
            'Нужно вввести UID карты, попробуй еще раз.\nДля выхода в главное меню нажмите /cancel')

    # освобождение памяти
    await state.finish()
