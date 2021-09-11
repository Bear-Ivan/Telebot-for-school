from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import add_card
from SQL.sqllite_db import sqllite
import re
from datetime import datetime
from Secret.config import max_count_chat_id, max_count_card_id


# from Secret.config import admin_id, bot_spam
# import requests

def DecToHex(codep: int):
    codep_hec = hex(codep).split('x')[-1][:-2]
    # print("Длина" + str(len(codep_hec)))
    if len(codep_hec) < 6:
        for x in range(6 - len(codep_hec)):
            codep_hec = "0" + codep_hec
    return codep_hec


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


@dp.message_handler(Command("add"), state=None)
async def enter_test(message: types.Message):
    db = sqllite()
    status_db, res = db.get_give(
        f"SELECT card_id from subscribers  WHERE telegramid_relationship ={int(message.from_user.id)}")
    if status_db:
        if len(res) > (max_count_card_id - 1):
            return await message.reply(
                f'У вас уже добавлено {max_count_card_id} карт для отслеживания. Больше добавлять нельзя.')
    else:
        return await message.reply(f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')

    await message.answer(
        "Введите UID(только цифры) карты, которую хотите отследить.\nUID можно узнать с помощью устройства, которое находится на вахте.\nЕсли у Вас зеленая карточка(с надписью 'Национальные проекты'), ее номер не совпадает с UID, Вам точно нужно обратиться на вахту.\nЕсли у Вас 'новая' белая карточка(она рабочая, открывает турникет) на ней есть цифры (10цифр), они совпадают с UID, можно на вахту не обращаться.\nНапример 1111111.\nДля выхода в главное меню нажмите /cancel")
    await add_card.Q1.set()


@dp.message_handler(state=add_card.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    cardid = check_number_Card(answer)

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif cardid:
        db = sqllite()
        status_db, res = db.get_give(f"SELECT telegramid_relationship from subscribers  WHERE card_id ={int(cardid)}")
        if status_db:
            if len(res) > (max_count_chat_id - 1):
                await state.reset_state()
                return await message.reply(
                    f'На данную карту уже подписаны {max_count_chat_id} человек. Больше добавлять нельзя.\nПроверить кто подписан можно по команде /check')
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')

        # провверяем если в БД такая карта
        st_db, res_db = sqllite().get_give(
            f"SELECT owner from pmark_code WHERE codep ='{str(DecToHex(cardid))}'")
        if st_db:
            # print(res_db)
            if len(res_db) == 1:
                # продолжаем
                await state.update_data(answer1=cardid)
            else:
                # await state.reset_state()
                return await message.reply(f'К сожалению, карты {cardid} не найдено в системе СКУД.\n'
                                           f'Проверьте правильность введеных цифр. Если цифры введены верно:\n'
                                           f'1.) Карта не добавлена в систему СКУД\n'
                                           f'2.) Не прошло 15 минут с момента добавления карты в систему СКУД. Синхронизация происходит один раз в 15 минут.\n'
                                           f'3.) Ввели неверный UID: перепроверьте UID с помощью устройства, которое находится на вахте.\n'
                                           f'Если не удалось решить проблему самостоятельно, воспользуйтесь обратной связью, попробую помочь.\n'
                                           f'Для выхода в главное меню нажмите /cancel')
        else:
            await state.reset_state()
            return await message.reply(
                f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')

    else:
        return await message.reply('Нужно вввести цифры попробуй еще раз. Для выхода в главное меню нажмите /cancel')
    # следующий вопрос
    await message.answer("Введите ФИО ребенка.\nДля выхода в главное меню нажмите /cancel")
    await add_card.next()


@dp.message_handler(state=add_card.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif len(answer) < 100:
        await state.update_data(answer2=answer)
    else:
        return await message.reply(
            'Ой, не более 100 символов БД не резиновая. Для выхода в главное меню нажмите /cancel')

    # следующий вопрос
    await message.answer(
        "Введите класс в котором учится ребенок. Например 1Д\nДля выхода в главное меню нажмите /cancel")
    await add_card.next()


@dp.message_handler(state=add_card.Q3)
async def answer_q3(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню')
    try:
        class_child = re.search(r'\d{1,2}[а-яА-ЯёЁ]', answer).group()
        await state.update_data(answer3=class_child.upper())
    except:
        return await message.reply(
            'Нужно ввести номер и букву класса ребенка(на русском языке). Для выхода в главное меню нажмите /cancel')

    # следующий вопрос
    await message.answer(
        "Введите кем вы являетесь ребенку. Например мать, отец, бабушка, дедушка ...\nДля выхода в главное меню нажмите /cancel")
    await add_card.next()


@dp.message_handler(state=add_card.Q4)
async def answer_q4(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif len(answer) < 50:
        await state.update_data(answer4=answer)
    else:
        return await message.reply(
            'Ой, не более 50 символов БД не резиновая. Для выхода в главное меню нажмите /cancel')

    # следующий вопрос
    await message.answer("Введите свое ФИО.\nДля выхода в главное меню нажмите /cancel")
    await add_card.next()


@dp.message_handler(state=add_card.Q5)
async def answer_q5(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == '/cancel':
        await state.reset_state()
        return await message.reply('Вышел в главное меню.')
    elif len(answer) < 100:
        # норм ответ идем дальше, а не в else
        answer5 = answer
    else:
        return await message.reply(
            'Ой, не более 100 символов БД не резиновая. Для выхода в главное меню нажмите /cancel')

    # Достаем переменные
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = data.get("answer2")
    answer3 = data.get("answer3")
    answer4 = data.get("answer4")
    text_answer = f"Карта {answer1} добавлена для отслеживания.\n" \
                  f"Ваши ответы:\n" \
                  f"Номер карты {answer1}\n" \
                  f"ФИО ребенка {answer2}\n" \
                  f"Класс {answer3}\n" \
                  f"Вы для ребенка {answer4}\n" \
                  f"Ваше ФИО {answer5}\n"

    text_answer_admin = f"telegtam id = {message.from_user.id}\n" \
                        f"teleramfullname = {message.from_user.full_name}\n" \
                        f"дата записи = {str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}"

    # работа с БД
    db = sqllite()
    db.connect()
    if db.check():
        _, count_zap = db.execute(
            f"SELECT card_id from subscribers WHERE telegramid_relationship ={int(message.from_user.id)} and card_id = {int(answer1)};")
        if len(count_zap) > 0:
            # Удаляю старые записи
            # print("Был дубль для /add")
            db.execute(
                f"DELETE FROM subscribers WHERE telegramid_relationship = {int(message.from_user.id)} and card_id ={int(answer1)};",
                commit=True)
        # запись в БД новой подписки
        result_db, _ = db.execute(
            f"INSERT INTO subscribers (card_id,fio_child,class,relationship,fio_relationship,telegramid_relationship,telegram_fullname,data_zapisi,need_send,card_uid_hex) "
            f"values('{int(answer1)}', '{str(answer2)}', '{str(answer3)}','{str(answer4)}','{str(answer5)}',{int(message.from_user.id)},'{str(message.from_user.full_name)}','{str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}',1,'{str(DecToHex(answer1))}')",
            commit=True)
        # print(f"INSERT INTO subscribers (card_id,fio_child,class,relationship,fio_relationship,telegramid_relationship,telegram_fullname,data_zapisi,need_send) values({int(answer1)}, {str(answer2)}, {str(answer3)},{str(answer4)},{str(answer5)},{int(message.from_user.id)},{str(message.from_user.full_name)},{str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))},1)")
        if result_db:
            # успех
            await message.answer(text_answer)
        else:
            # отпрака админу что авторизация не удалась
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')
    else:
        # отпрака админу что авторизация не удалась
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'ОЙ, что-то с нашей БД. Попробуйте позже. Уже сообщил админу, скоро все починят.')

    db.close()

    # освобождение памяти
    await state.finish()
