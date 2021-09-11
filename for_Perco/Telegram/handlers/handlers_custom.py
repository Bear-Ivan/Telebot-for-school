from Telegram.loader import dp, bot
from aiogram.types import Message
from Secret.config import hello, list_commands, list_commands_admin, admin_id,bot_spam
from aiogram.dispatcher.filters import Command
import time
from SQL.sqllite_db import sqllite
# import requests

async def send_to_Admin(dp):
    await bot.send_message(chat_id=admin_id, text='Бот запущен')


# @dp.message_handler()
# async def echo(message:Message):
#     # time.sleep(30)
#     text = f"Привет ты написал '<b><i>{message.text} </i></b>'дата {message.date} first name {message.from_user.first_name} full name {message.from_user.full_name}"
#     await bot.send_message(chat_id = message.from_user.id, text = text)
#     # await message.answer(text = 'ансвер')

# спать

@dp.message_handler(Command("sleep"))
async def Hello(message: Message):
    if (message.from_user.id == admin_id):
        try:
            minute = int(message.get_args())
        except:
            return await message.reply(f"Ой, похоже вы забыли аргумент.\nНапример /sleep 1 - засну на 1 минуту")
        await message.reply(f"Засыпаю на {minute} минуту")
        time.sleep(minute*60)
        await message.answer("Проснулся")

# сount
@dp.message_handler(Command("count"))
async def Hello(message: Message):
    if (message.from_user.id == admin_id):
        db = sqllite()
        status_db, res = db.get_give(
            f"SELECT COUNT(DISTINCT card_id) as count_cardid, COUNT(DISTINCT telegramid_relationship) as count_people from subscribers  WHERE need_send=1;")
        if status_db:
            await message.reply(f"Количество карт поставленное на отслеживание = {res[0]['count_cardid']}\n"
                                f"Количество людей которые пользуются ботом = {res[0]['count_people']}\n")

# # reviews
# @dp.message_handler(Command("reviews"))
# async def Hello(message: Message):
#     # переделай на FSM
#     review = message.get_args()
#     review_full = f'От: chatid = {message.from_user.id}\n ФИО телеграмм = {message.from_user.full_name}\n Сообщение:"{message.get_args()}"'
#     #
#     params_spambot = {'chat_id': admin_id, 'text': review_full}
#     response_spam = requests.post(bot_spam + 'sendMessage', data=params_spambot, timeout=30)
#     if response_spam.status_code == 200:
#         await bot.send_message(chat_id=message.from_user.id, text=f'Ваше сообщение: <i>"{review}"</i> успешно отправлено админу.')
#     else:
#         await bot.send_message(chat_id=message.from_user.id, text=f"Ой, что-то пошло не так. Попробуйте позже.")


#     Приветствие
# кнопка старт и помощь


@dp.message_handler(commands=["start", "?", "помощь", "help"])
async def Hello(message: Message):
    await bot.send_message(chat_id=message.from_user.id, text=hello)
    await bot.send_message(chat_id=message.from_user.id, text=list_commands)
    if (message.from_user.id == admin_id):
        await bot.send_message(chat_id=message.from_user.id, text=list_commands_admin)


# в тексте знак
@dp.message_handler()
async def Hello(message: Message):
    text = message.text
    if text == '?':
        await bot.send_message(chat_id=message.from_user.id, text=hello)
        await bot.send_message(chat_id=message.from_user.id, text=list_commands)
        if (message.from_user.id == admin_id):
            await bot.send_message(chat_id=message.from_user.id, text=list_commands_admin)


@dp.message_handler(Command("sleep"))
async def Hello(message: Message):
    if (message.from_user.id == admin_id):
        try:
            minute = int(message.get_args())
        except:
            return await bot.send_message(chat_id=message.from_user.id, text=f"Ой, похоже вы забыли аргумент.\n Например /sleep 1 - засну на 1 минуту")
        await bot.send_message(chat_id=message.from_user.id, text=f"Засыпаю на {minute} минуту")
        time.sleep(minute*60)
        await bot.send_message(chat_id=message.from_user.id, text="Проснулся")
