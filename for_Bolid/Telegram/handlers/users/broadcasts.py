from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import broadcast
from SQL.sqllite_db import sqllite
from Secret.config import admin_id


@dp.message_handler(Command("broadcast"), state=None)
async def enter_test(message: types.Message):
    if (message.from_user.id == admin_id):
        await message.answer(
            'Вы уверены что хотите разослать всем пользователям сообщение?\nНапиши да или нет.\nДля выхода в главное меню нажмите /cancel')
        await broadcast.Q1.set()


@dp.message_handler(state=broadcast.Q1)
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
            await state.update_data(answer1=answer)
        else:
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')

        # Следующий вопрос
        await message.answer(
            "Введите сообщение, которое будет разослано всем.\nДля выхода в главное меню нажмите /cancel")
        await broadcast.next()


@dp.message_handler(state=broadcast.Q2)
async def answer_q1(message: types.Message, state: FSMContext):
    if (message.from_user.id == admin_id):
        answer = message.text
        if answer == '/cancel':
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')
        # подключаемся к БД
        # Всем сообщение о начале нового учебного года.
        status_db, res = sqllite().get_give(
            "SELECT DISTINCT telegramid_relationship from subscribers WHERE need_send=1;")
        er = ""
        if status_db:
            for mes in res:
                try:
                    await bot.send_message(chat_id=int(mes['telegramid_relationship']), text=answer)
                except:
                    er += f"Не смог отправить для chatid = {int(mes['telegramid_relationship'])}\n"
            # ответ админу
            if er:
                await message.answer(f"Собщение всем подписчикам разослал, кроме:\n {er}")
            else:
                await message.answer("Собщение всем подписчикам разослал успешно.")
        else:
            return await message.reply('Ой, что-то не так c нашей БД на этапе execute. Попробуйте позже.')

        # освобождение памяти
        await state.finish()
