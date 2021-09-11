from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from Telegram.loader import dp, bot
from Telegram.states.question import answerr
from Secret.config import admin_id
import re

@dp.message_handler(Command("answer"), state=None)
async def enter_test(message: types.Message):
    if (message.from_user.id == admin_id):
        await message.answer(
            'Введите Id пользователя которому хотите переслать сообщение. Только цифры\nДля выхода в главное меню нажмите /cancel')
        await answerr.Q1.set()


@dp.message_handler(state=answerr.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    if (message.from_user.id == admin_id):
        answer = message.text
        if answer == '/cancel':
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')
        try:
            id_telega = re.search(r'\d+', answer).group()
            await state.update_data(answer1=id_telega)
        except:
            return await message.reply('Нужно вводить только цифры.\nДля выхода в главное меню нажмите /cancel')

        # Следующий вопрос
        await message.answer(f"Введите сообщение, которое будет отправлено пользователю с id={id_telega}.\nДля выхода в главное меню нажмите /cancel")
        await answerr.next()

@dp.message_handler(state=answerr.Q2)
async def answer_q1(message: types.Message, state: FSMContext):
    if (message.from_user.id == admin_id):
        answer = message.text
        if answer == '/cancel':
            await state.reset_state()
            return await message.reply('Вышел в главное меню.')

        # Достаем переменные
        data = await state.get_data()
        answer1 = data.get("answer1")
        answer2 = "Вам сообщение от администратора:\n" + answer

        await bot.send_message(chat_id=int(answer1), text=answer2)
        await message.reply("Сообщение отправлено.")

        # освобождение памяти
        await state.finish()
