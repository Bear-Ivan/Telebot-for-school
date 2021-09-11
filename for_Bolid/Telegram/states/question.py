from aiogram.dispatcher.filters.state import StatesGroup, State


class add_card(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()

class check_card(StatesGroup):
    Q1 = State()

class delete_card(StatesGroup):
    Q1 = State()

class review(StatesGroup):
    Q1 = State()

class reset(StatesGroup):
    Q1 = State()

class prolongation(StatesGroup):
    Q1 = State()
    Q2 = State()

class broadcast(StatesGroup):
    Q1 = State()
    Q2 = State()

class answerr(StatesGroup):
    Q1 = State()
    Q2 = State()

class history_card(StatesGroup):
    Q1 = State()




