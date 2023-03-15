#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import logging

from synopsis.config.settings import settings
from synopsis.db.database import DataBase
from synopsis.config.users import users as userType
from synopsis.config.events import events

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

class Searching(StatesGroup):
    READY = State()

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

search_cb = CallbackData('search', 'key', 'value')

@dp.callback_query_handler(search_cb.filter(), state="*")
async def process_search_filters(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    key = callback_data.get('key')
    value = int(callback_data.get('value'))
    msg = call.message.reply_markup.inline_keyboard[value-1][0].text

    async with state.proxy() as data:
        data[key] = value

    res = db.get_events(await state.get_data())
    await call.answer(f'Найдено мероприятий: {len(res)}')
    await call.message.edit_text(msg, reply_markup=None)

@dp.message_handler(Text(equals=["Поиск мероприятий"]), state="*")
async def search_events_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Время начала"),
                KeyboardButton(text="Дата начала"),
            ],
            [
                KeyboardButton(text="Тип мероприятия"),
            ],
            [
                KeyboardButton(text="Продолжительность"),
            ],
            [
                KeyboardButton(text="Показать"),
                KeyboardButton(text="Сбросить"),
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )
    await Searching.READY.set()
    await message.reply("Выберите характеристику:", reply_markup=markup)

@dp.message_handler(Text(equals=["Время начала"]), state=Searching.READY)
async def choose_time_start(message: types.Message):
    time_start = InlineKeyboardMarkup(row_width=1)
    before_12 = InlineKeyboardButton('До 12', callback_data=search_cb.new(key='start_time', value=events.time.before_12.value))
    between_12_16 = InlineKeyboardButton('С 12 до 16', callback_data=search_cb.new(key='start_time', value=events.time.between_12_16.value))
    between_16_19 = InlineKeyboardButton('С 16 до 19', callback_data=search_cb.new(key='start_time', value=events.time.between_16_19.value))
    after_19 = InlineKeyboardButton('Позднее 19', callback_data=search_cb.new(key='start_time', value=events.time.after_19.value))
    time_start.add(before_12, between_12_16, between_16_19, after_19)
    await message.reply("Выберите время начала:", reply_markup=time_start)

@dp.message_handler(Text(equals=["Дата начала"]), state=Searching.READY)
async def choose_date_start(message: types.Message):
    date_start = InlineKeyboardMarkup(row_width=1)
    today = InlineKeyboardButton('Сегодня', callback_data=search_cb.new(key='event_date', value=events.date.today.value))
    tommorow = InlineKeyboardButton('Завтра', callback_data=search_cb.new(key='event_date', value=events.date.tomorrow.value))
    next_week = InlineKeyboardButton('Ближайшая неделя', callback_data=search_cb.new(key='event_date', value=events.date.next_week.value))
    date_start.add(today, tommorow, next_week)
    await message.reply("Выберите дату начала:", reply_markup=date_start)

@dp.message_handler(Text(equals=["Продолжительность"]), state=Searching.READY)
async def choose_duration(message: types.Message):
    duratiion = InlineKeyboardMarkup(row_width=1)
    min_30 = InlineKeyboardButton('~30', callback_data=search_cb.new(key='duration', value=events.duration.min_30.value))
    hour_1 = InlineKeyboardButton('~1:00', callback_data=search_cb.new(key='duration', value=events.duration.hour_1.value))
    hour_1_30 = InlineKeyboardButton('~1:30', callback_data=search_cb.new(key='duration', value=events.duration.hour_1_30.value))
    hour_2 = InlineKeyboardButton('~2:00', callback_data=search_cb.new(key='duration', value=events.duration.hour_2.value))
    hour_3 = InlineKeyboardButton('~3:00', callback_data=search_cb.new(key='duration', value=events.duration.hour_3.value))
    more_3 = InlineKeyboardButton('Более 3 часов', callback_data=search_cb.new(key='duration', value=events.duration.more_3.value))
    duratiion.add(min_30, hour_1, hour_1_30, hour_2, hour_3, more_3)
    await message.reply("Выберите продоолжительность:", reply_markup=duratiion)

@dp.message_handler(Text(equals=["Тип мероприятия"]), state=Searching.READY)
async def choose_type(message: types.Message):
    event_type = InlineKeyboardMarkup(row_width=1)
    sport = InlineKeyboardButton('Спорт', callback_data=search_cb.new(key='event_type', value=events.type.sport.value))
    education = InlineKeyboardButton('Образование', callback_data=search_cb.new(key='event_type', value=events.type.education.value))
    culture = InlineKeyboardButton('Культура', callback_data=search_cb.new(key='event_type', value=events.type.culture.value))
    event_type.add(sport, education, culture)
    await message.reply("Выберите тип мероприятия:", reply_markup=event_type)

@dp.message_handler(Text(equals=["Показать"]), state=Searching.READY)
async def show_events(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data)

    # строим запрос к базе данных и получаем список мероприятий, соответствующих выбранным характеристикам
    events = db.get_events(await state.get_data())

    # отображаем найденные мероприятия
    if not events:
        await message.answer("Ничего не найдено. Фильтры поиска сброшены")
        await state.finish()
        await Searching.READY.set()
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

        await message.answer(events_text)

@dp.message_handler(Text(equals=["Сбросить"]), state=Searching.READY)
async def wipe_filters(message: types.Message, state: FSMContext):
    await state.finish()
    await Searching.READY.set()
    await message.answer("Фильтры поиска сброшены")


@dp.message_handler(Text(equals=["Назад"]), state="*")
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()
    markup = get_main_keyboard(user_type=int(db.get_user(message.from_id)[2]))
    await message.answer("Выберите действие:", reply_markup=markup)


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


@dp.message_handler(Text(equals=["Добавить в избранное"]))
async def add_to_favorites(message: types.Message):
    # строим запрос на добавление мероприятия в избранное
    await message.answer("Мероприятие добавлено в избранное")


@dp.message_handler(Text(equals=["Удалить из избранного"]))
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