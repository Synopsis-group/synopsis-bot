#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

import logging

from synopsis.config.settings import settings
from synopsis.db.database import DataBase
from synopsis.config.users import users as userType

logger = logging.getLogger('logger')


bot = Bot(token=settings.bots.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db: DataBase = DataBase()

cities = [
    "Новоуральск",
    "Екатеринбург"
]

class SearchEvents(StatesGroup):
    time_start = State()
    date_start = State()
    duration = State()
    organization = State()
    event_type = State()
    create_type = State()
def get_main_keyboard(user_type):
    if user_type == userType.owner or user_type == userType.admin:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поиск мероприятий"),
                ],
                [
                    KeyboardButton(text="Управление событиями"),
                ],
                [
                    KeyboardButton(text="Избранное"),
                    KeyboardButton(text="Другое"),
                ],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поиск мероприятий"),

                ],
                [
                    KeyboardButton(text="Избранное"),
                    KeyboardButton(text="Другое"),
                ],
            ],
            resize_keyboard=True,
        )


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    # Проверяем, является ли пользователь админом
    user = db.get_user(message.from_id)
    if not user:
        db.insert_user([message.from_id, userType.user.value])
        user = (None, None, userType.user)
    user_type = int(user[2])
    logger.debug(f"{message.from_id} is {user_type}")

    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard(user_type),
    )


@dp.message_handler(Text(equals=["Поиск мероприятий"]))
async def search_events_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Время начала"),
                KeyboardButton(text="Дата начала"),
            ],
            [
                KeyboardButton(text="Продолжительность"),
                KeyboardButton(text="Организация"),
            ],
            [
                KeyboardButton(text="Тип мероприятия"),
            ],
            [
                KeyboardButton(text="Сбросить"),
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите характеристику:", reply_markup=markup)
    await SearchEvents.time_start.set()


@dp.message_handler(Text(equals=["Назад"]), state="*")
async def go_back(message: types.Message, state: FSMContext):
    markup = get_main_keyboard(user_type="admin" if message.from_user.username in ["admin1", "admin2"] else "user")

    await message.answer("Выберите действие:", reply_markup=markup)
    await state.reset_state()


@dp.message_handler(Text(equals=["Время начала"]), state=SearchEvents.time_start)
async def choose_time_start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="До 12"),
                KeyboardButton(text="С 12 до 18"),
            ],
            [
                KeyboardButton(text="С 16 до 19"),
                KeyboardButton(text="Позднее 19"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите время начала:", reply_markup=markup)
    await SearchEvents.next()


@dp.message_handler(Text(equals=["До 12", "С 12 до 18", "С 16 до 19", "Позднее 19", "Назад"]), state=SearchEvents.time_start)
async def get_time_start(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return

    await state.update_data(time_start=message.text)
    markup = ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Сегодня"),
                KeyboardButton(text="Завтра"),
            ],
            [
                KeyboardButton(text="Ближайшая неделя"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите дату начала:", reply_markup=markup)
    await SearchEvents.date_start.set()


@dp.message_handler(Text(equals=["Сегодня", "Завтра", "Ближайшая неделя", "Назад"]), state=SearchEvents.date_start)
async def get_date_start(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return

    await state.update_data(date_start=message.text)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="~30"),
                KeyboardButton(text="~1:00"),
            ],
            [
                KeyboardButton(text="~1:30"),
                KeyboardButton(text="~2:00"),
                KeyboardButton(text="~2:30"),
            ],
            [
                KeyboardButton(text="~3:00"),
                KeyboardButton(text="Более 3 ч"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите продолжительность:", reply_markup=markup)
    await SearchEvents.duration.set()


@dp.message_handler(Text(equals=["~30", "~1:00", "~1:30", "~2:00", "~2:30", "~3:00", "Более 3 ч", "Назад"]), state=SearchEvents.duration)
async def get_duration(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return

    await state.update_data(duration=message.text)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="СЮТ"),
                KeyboardButton(text="НЕЙВА"),
            ],
            [
                KeyboardButton(text="ДЮСШ"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите организацию:", reply_markup=markup)
    await SearchEvents.organization.set()


@dp.message_handler(Text(equals=["СЮТ", "НЕЙВА", "ДЮСШ", "Назад"]), state=SearchEvents.organization)
async def get_organization(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return

    await state.update_data(organization=message.text)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Спорт"),
                KeyboardButton(text="Образование"),
            ],
            [
                KeyboardButton(text="Культура"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите тип мероприятия:", reply_markup=markup)
    await SearchEvents.event_type.set()


@dp.message_handler(Text(equals=["Спорт", "Образование", "Культура", "Назад"]), state=SearchEvents.event_type)
async def get_event_type(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return

    await state.update_data(event_type=message.text)
    # получаем сохраненные данные
    data = await state.get_data()

    # отображаем выбранные характеристики
    text = "Выбранные характеристики:\n"
    for key, value in data.items():
        # убираем префикс "SearchEvents." в начале названия состояния
        text += f"{key[12:].replace('_', ' ').capitalize()}: {value}\n"

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Показать"),
                KeyboardButton(text="Сбросить"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer(text, reply_markup=markup)
    await SearchEvents.next()


@dp.message_handler(Text(equals=["Показать"]), state=SearchEvents.event_type)
async def show_events(message: types.Message, state: FSMContext):
    # получаем сохраненные данные
    data = await state.get_data()

    # строим запрос к базе данных и получаем список мероприятий, соответствующих выбранным характеристикам
    events = []

    # отображаем найденные мероприятия
    if len(events) == 0:
        await message.answer("Ничего не найдено")
        await state.reset_state()
        return
    else:
        events_text = "Найденные мероприятия:\n\n"
        for event in events:
            events_text += (
                f"[{event['id']}] {event['name']}\n"
                f"Тип: {event['type']}\n"
                f"Дата: {event['date']}\n"
                f"Время: {event['time']}\n"
                f"Организация: {event['organization']}\n"
                f"Добавил: {event['admin']}\n\n"
            )

        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Добавить в избранное"),
                    KeyboardButton(text="Назад"),
                ],
            ],
            resize_keyboard=True,
        )

        await message.answer(events_text, reply_markup=markup)
        await SearchEvents.next()


@dp.message_handler(Text(equals=["Сбросить"]), state=SearchEvents.event_type)
async def reset_search(message: types.Message, state: FSMContext):
    await message.answer("Поиск сброшен")
    await state.reset_state()
    await cmd_start(message)


@dp.message_handler(Text(equals=["Избранное"]))
async def favorites_handler(message: types.Message):
    # строим запрос к базе данных и получаем список избранных мероприятий
    favorites = []

    if len(favorites) == 0:
        await message.answer("Избранное пусто")
        return
    else:
        favorites_text = "Избранное:\n\n"
        for favorite in favorites:
            favorites_text += (
                f"[{favorite['id']}] {favorite['name']}\n"
                f"Тип: {favorite['type']}\n"
                f"Дата: {favorite['date']}\n"
                f"Время: {favorite['time']}\n"
                f"Организация: {favorite['organization']}\n"
                f"Добавил: {favorite['admin']}\n\n"
            )

        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Удалить из избранного"),
                    KeyboardButton(text="Назад"),
                ],
            ],
            resize_keyboard=True,
        )

        await message.answer(favorites_text, reply_markup=markup)


@dp.message_handler(Text(equals=["Добавить в избранное"]), state="*")
async def add_to_favorites(message: types.Message):
    # строим запрос на добавление мероприятия в избранное
    await message.answer("Мероприятие добавлено в избранное")


@dp.message_handler(Text(equals=["Удалить из избранного"]), state="*")
async def remove_from_favorites(message: types.Message):
    # строим запрос на удаление мероприятия из избранного
    await message.answer("Мероприятие удалено из избранного")


@dp.message_handler(Text(equals=["Другое"] + cities))
async def other_handler(message: types.Message):
    if message.text in cities:
        logger.debug(f"user {message.from_id} выбрал город {message.text}")
        db.update_user_city(message.from_id, message.text)
        await message.reply("Город установлен")

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Подписки"),
                KeyboardButton(text="Настройки"),
            ],
            [
                KeyboardButton(text="FAQ"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите действие:", reply_markup=markup)
    logger.debug("Выбрано другое")


@dp.message_handler(Text(equals=["FAQ"]))
async def faq_handler(message: types.Message):
    await message.answer("Ссылка на FAQ: https://telegra.ph/FAQ-11-25")
    logger.debug("Выбрано FAQ")


@dp.message_handler(Text(equals=["Подписки"]))
async def faq_handler(message: types.Message):
    await message.answer("В разработке")
    logger.debug("Выбрано Подписки")


@dp.message_handler(Text(equals=["Настройки"]))
async def settings_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Город проживания"),
            ],
            [
                KeyboardButton(text="Другое"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите настройку:", reply_markup=markup)

@dp.message_handler(Text(equals=["Город проживания"]))
async def choose_city(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=city)] for city in cities
        ],
        resize_keyboard=True,
    )
    city = db.get_user(message.from_id)[3]
    if not city: city = "не установлено"
    await message.answer(f"Выберите город\n(текущий: {city})", reply_markup=markup)

def start():
    logger.debug(f"Bot has been started")
    executor.start_polling(dp, skip_updates=True)










@dp.message_handler(Text(equals=["Управление событиями"]))
async def search_events_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Создать"),
                KeyboardButton(text="Изменить"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите настройки для создания:", reply_markup=markup)
    await SearchEvents.create_type.set()


@dp.message_handler(Text(equals=["Создать"]), state=SearchEvents.create_type)
async def choose_time_start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Название мероприятия"),
                KeyboardButton(text="Тип мероприятия"),
            ],
            [
                KeyboardButton(text="Время начала"),
                KeyboardButton(text="Дата проведения"),
            ],
            [
                KeyboardButton(text="Продолжительность"),
                KeyboardButton(text="Организация"),
            ],
            [
                KeyboardButton(text="Назад"),
            ]
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите соответствующие характеристики:", reply_markup=markup)
    await SearchEvents.event_type.set()

@dp.message_handler(Text(equals=["Тип мероприятия"]), state=SearchEvents.event_type)
async def choose_event_type(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Спорт"),
                KeyboardButton(text="Образование"),
            ],
            [
                KeyboardButton(text="Культура"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите тип мероприятия:", reply_markup=markup)
    await SearchEvents.next()


@dp.message_handler(Text(equals=["Спорт", "Образование", "Культура", "Назад"]), state=SearchEvents.event_type)
async def get_event_type(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await go_back(message, state)
        return
    await state.update_data(event_type=message.text)