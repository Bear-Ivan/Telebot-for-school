# BOT
BOT_TOKEN = "1I"
bot_spam = "https://api.telegram.org/bot6Nw/"
admin_id = 1111111
# максимальное количество чатов в которые отсылается информация от cardid. те 1 ребенка можно отслеживать не более 5 родственникам.
max_count_chat_id = 5
# максимальное количество карт для одного чата id. те один человек не может подписаться более чем на 5 карт.
max_count_card_id = 5
hello = "Доброго времени суток.\n" \
        "Данный бот информирует родителей (законных представителей) о прохождении учащихся лицея через турникет.\n" \
        "Нажимая кнопку добавить, вы соглашаетесь, что данный сервис не гарантирует нахождение ребенка в лицее, или что он вышел из лицея.\n" \
        "<b>Претензий к лицею по данному сервису не имею.</b>"
list_commands = f"/help - описание бота и что он умеет.\n" \
                f"/add - подписаться на оповещение о проходе учащегося через турникет.\n" \
                f"/check - проверить кто подписан на карту учащегося. Можно подписать до {max_count_card_id} человек.\n" \
                f"/delete - отписаться от оповещения.\n" \
                f"/reviews - отзывы и предложения."
list_commands_admin = "/count - количество людей которые подписались.\n" \
                      "/sleep - спасть в минутах, останавливает работу бота.\n" \
                      "/reset - сбросить все подписки и выслать предложение на продление для всех.\n" \
                      "/broadcast - разослать всем подписчикам бота сообщение.\n" \
                      "/answer - ответить пользователю."

PATH_FBDB = 'C:\\BasePerco\\SCD17K.FDB'
LOGIN_FBDB = ''
PASS_FBDB = ''
# количество секундж между опросами СКУД системы
sleep_FBDB = 30
# количество дней для продления подписки
reset_podpiska = 3
