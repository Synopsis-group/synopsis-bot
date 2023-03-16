#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import bold, text

import logging

from synopsis.config.settings import settings
from synopsis.db.database import DataBase
from synopsis.config.users import users as userType
from synopsis.config.events import events

logger = logging.getLogger('logger')


bot = Bot(token=settings.bots.token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db: DataBase = DataBase()

cities = [
    "Новоуральск",
]

class CreateEvent(StatesGroup):
    title = State()
    event_type = State()
    start_time = State()
    event_date = State()
    duration = State()
    organization = State()

class SearchEvents(StatesGroup):
    READY = State()

class Back(StatesGroup):
    Main = State()
    Others = State()
    Settings = State()
    City = State()
    Admins = State()
    Reg = State()
    Events = State()

class ManageAdmin(StatesGroup):
    admin_remove = State()
    admin_add = State()

class ManageEvent(StatesGroup):
    event_cancel = State()
    event_finish = State()

def get_main_keyboard(user_type):
    if user_type == -1:
        logger.debug("<b>Город проживания не установлен</b>")
        return ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Город проживания"),
                        ],
                    ],
                    resize_keyboard=True,
                )

    if user_type == userType.admin or user_type == userType.owner:
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

async def open_main_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await Back.Main.set()
    markup = get_main_keyboard(user_type=int(db.get_user(message.from_id)[3]))
    await message.answer("<b>Выберите действие:</b>", reply_markup=markup)

@dp.message_handler(commands=["start"], state="*")
async def cmd_start(message: types.Message):
    # Проверяем, является ли пользователь админом
    await Back.Main.set()
    msg = "<b>Выберите действие:</b>"
    user = db.get_user(message.from_id)
    if not user:
        db.insert_user([message.from_id, message.from_user.username, userType.user.value])
        user = (None, None, None, userType.user, None)
    user_type = int(user[3])
    if not user[4]:
        user_type = -1
        msg = "Пройдите <b>первичную</b> настройку"
        await Back.Reg.set()
    logger.debug(f"{message.from_id} is {user_type}")

    await message.answer(
        msg,
        reply_markup=get_main_keyboard(user_type),
    )

search_cb = CallbackData('search', 'key', 'value')

@dp.callback_query_handler(search_cb.filter(), state=SearchEvents.READY)
async def process_search_filters(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    key = callback_data.get('key')
    value = int(callback_data.get('value'))
    msg = ''
    if key == 'start_time': msg = events.time(value).description
    if key == 'event_date': msg = events.date(value).description
    if key == 'duration': msg = events.duration(value).description
    if key == 'event_type': msg = events.type(value).description

    async with state.proxy() as data:
        data[key] = value
    res = db.get_events(await state.get_data())
    await call.answer(f'Найдено мероприятий: {len(res)}')
    await call.message.edit_text(msg, reply_markup=None)

@dp.message_handler(Text(equals=["Поиск мероприятий"]), state=Back.Main)
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
    print(message)
    await SearchEvents.READY.set()
    await message.reply("<b>Выберите характеристику:</b>", reply_markup=markup)

@dp.message_handler(Text(equals=["Время начала"]), state=SearchEvents.READY)
async def choose_time_start(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.time.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=search_cb.new(key='start_time', value=obj.value)))
    await message.reply("Выберите время начала:", reply_markup=options)

@dp.message_handler(Text(equals=["Дата начала"]), state=SearchEvents.READY)
async def choose_date_start(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.date.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=search_cb.new(key='event_date', value=obj.value)))
    await message.reply("Выберите дату начала:", reply_markup=options)

@dp.message_handler(Text(equals=["Продолжительность"]), state=SearchEvents.READY)
async def choose_duration(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.duration.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=search_cb.new(key='duration', value=obj.value)))
    await message.reply("Выберите продоолжительность:", reply_markup=options)

@dp.message_handler(Text(equals=["Тип мероприятия"]), state=SearchEvents.READY)
async def choose_type(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.type.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=search_cb.new(key='event_type', value=obj.value)))
    await message.reply("<b>Выберите тип мероприятия:</b>", reply_markup=options)

@dp.message_handler(Text(equals=["Показать"]), state=SearchEvents.READY)
async def show_events(message: types.Message, state: FSMContext):
    # строим запрос к базе данных и получаем список мероприятий, соответствующих выбранным характеристикам
    data = await state.get_data()
    data['event_status'] = events.status.new
    events_list = db.get_events(data)

    # отображаем найденные мероприятия
    if not events_list:
        await message.answer("Ничего не найдено. Фильтры поиска сброшены")
        await state.finish()
        await SearchEvents.READY.set()
    else:
        events_text = "Найденные мероприятия:\n"
        for event in events_list:
            events_text += f"""
[<code>{event[0]}</code>] {event[7].strip()}
Тип: {events.type(event[8]).description}
Дата: {events.date(event[10]).description}
Время: {events.time(event[9]).description}
Организация: {event[12]}
Продолжительность: {events.duration(event[10]).description}
Добавил: @{event[3]}\n
            """
        await message.answer(events_text)

@dp.message_handler(Text(equals=["Сбросить"]), state=SearchEvents.READY)
async def wipe_filters(message: types.Message, state: FSMContext):
    await state.finish()
    await SearchEvents.READY.set()
    await message.answer("Фильтры поиска сброшены")

@dp.message_handler(Text(equals=["Назад"]), state=SearchEvents.READY)
async def go_back_search(message: types.Message, state: FSMContext):
    logger.debug("Back search")
    await open_main_menu(message, state)


@dp.message_handler(Text(equals=["Назад"]), state=[Back.Others, Back.Events])
async def go_back_others(message: types.Message, state: FSMContext):
    logger.debug("Back others or manage events")
    await open_main_menu(message, state)

@dp.message_handler(Text(equals=["Назад", "Отменить"]), state=[Back.Settings, Back.Admins] + list(ManageAdmin.states))
async def go_back_settings(message: types.Message):
    logger.debug("Back settings or manage admins")
    await other_handler(message)


@dp.message_handler(Text(equals=["Избранное"]), state=Back.Main)
async def favorites_handler(message: types.Message):
    await message.answer("В разработке")
    logger.debug("Выбрано Избранное")

@dp.message_handler(Text(equals=["Другое"]), state=Back.Main)
async def other_handler(message: types.Message):
    await Back.Others.set()
    user = db.get_user(message.from_id)
    user_type = int(user[3])
    if user_type == userType.owner:
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
                KeyboardButton(text="Управление админами"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )
    else:
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
    await message.answer("<b>Выберите действие:</b>", reply_markup=markup)
    logger.debug("Выбрано другое")

@dp.message_handler(Text(equals=["FAQ"]), state=Back.Others)
async def faq_handler(message: types.Message):
    await message.answer("Ссылка на FAQ: <a href='https://telegra.ph/FAQ---CHasto-zadavaemye-voprosy-i-otvety-na-nih-03-16'>нажми сюда</a>")
    logger.debug("Выбрано FAQ")

@dp.message_handler(Text(equals=["Подписки"]), state=Back.Others)
async def subs_handler(message: types.Message):
    await message.answer("В разработке")
    logger.debug("Выбрано Подписки")


@dp.message_handler(Text(equals=["Настройки"]), state=Back.Others)
async def settings_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Город проживания"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )
    await Back.Settings.set()
    await message.answer("<b>Выберите настройку:</b>", reply_markup=markup)

@dp.message_handler(Text(equals=cities), state=Back.City)
async def city_handler(message: types.Message):
    logger.debug("Back city")
    logger.debug(f"user {message.from_id} выбрал город {message.text}")
    db.update_user(message.from_id, {"city": message.text})
    await message.reply("Город установлен")
    await other_handler(message)

@dp.message_handler(Text(equals=cities), state=Back.Reg)
async def reg(message: types.Message, state: FSMContext):
    logger.debug("Back Reg")
    logger.debug(f"user {message.from_id} выбрал город {message.text}")
    db.update_user(message.from_id, {"city": message.text})
    await message.reply("Город установлен")
    await message.answer("Первичная настройка выполнена! Приятного пользования")
    await open_main_menu(message, state)

@dp.message_handler(Text(equals=["Город проживания"]), state=[Back.Settings, Back.Reg])
async def choose_city(message: types.Message, state=FSMContext):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=city)] for city in cities
        ],
        resize_keyboard=True,
    )
    city = db.get_user(message.from_id)[4]
    if not city: city = "не установлено"
    await message.answer(f"Выберите город\n(текущий: {city})", reply_markup=markup)
    if await state.get_state() != Back.Reg.state:
        await Back.City.set()


@dp.message_handler(Text(equals=["Управление админами"]), state=Back.Others)
async def admin_manage(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить"), KeyboardButton(text="Удалить"),
            ],
            [
                KeyboardButton(text="Назад"),
            ]
        ],
        resize_keyboard=True,
    )
    await Back.Admins.set()
    msg = f"<i>Всего пользователей:</i> {len(db.get_users())}"
    msg += "\n<b>Текущие админы:\n</b>"
    for i, obj in enumerate(db.get_users(userType.admin.value)):
        msg += f"{i+1}. @{obj[1]} : <code>{obj[0]}</code>\n"

    msg += "<b>\n Обычные пользователи:\n</b>"
    for i, obj in enumerate(db.get_users(userType.user.value)):
        msg += f"{i+1}. @{obj[1]} : <code>{obj[0]}</code>\n"

    await message.answer(msg, reply_markup=markup)
    await message.answer("<b>Выберите действие:</b>")

@dp.message_handler(Text(equals=["Удалить"]), state=Back.Admins)
async def remove_admin(message: types.Message):
    await ManageAdmin.admin_remove.set()
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отменить")
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Вставьте <i>id пользователя</i>, которого вы хотите удалить из адимнов", reply_markup=markup)

@dp.message_handler(Text(equals=["Добавить"]), state=Back.Admins)
async def add_admin(message: types.Message):
    await ManageAdmin.admin_add.set()
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отменить")
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Вставьте <i>id пользователя</i>, которого вы хотите добавить в админы", reply_markup=markup)

@dp.message_handler(state=list(ManageAdmin.states))
async def handle_admin(message: types.Message, state: FSMContext):
    logger.debug(f"Remove or add user {message.text}")
    if any(message.text == str(obj[0]) for obj in db.get_users(userType.owner.value)):
        await message.reply("Самый хитрый? Ты не можешь понизить владельца")
        return
    r = -1
    if await state.get_state() == ManageAdmin.admin_add.state:
        r = db.update_user(message.text, {"parent_id": message.from_id, "user_role": userType.admin})
        if r > 0:
            await message.reply("Пользователь успешно повышен")
            await bot.send_message(int(message.text), "Вы были назначены на роль <b>администратора</b>.\nПерезапустите бота командой /start")
    else:
        r = db.update_user(message.text, {"parent_id": message.from_id, "user_role": userType.user})
        if r > 0:
            await message.reply("Пользователь успешно понижен")
            await bot.send_message(int(message.text), "Вы были сняты с роли <b>администратора</b>.\nПерезапустите бота командой /start")
    if r == -1: await message.reply("Невозможно выполнить операцию")
    if r == 0: await message.reply("Пользователь с данным id <b>не зарегистрирован</b> в боте")
    await other_handler(message)


markup_manage_event = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать"), KeyboardButton(text="Показать"),
        ],
        [
            KeyboardButton(text="Удалить"), KeyboardButton(text="Завершить"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ],
    resize_keyboard=True,
)

@dp.message_handler(Text(equals=["Управление событиями"]), state=Back.Main)
async def event_manage(message: types.Message):
    user = db.get_user(message.from_id)
    user_type = int(user[3])
    if user_type == userType.user:
        await message.answer("Доступ <b>заблокирован</b>: вы не являетесь администратором")
        return
    await Back.Events.set()
    await message.answer("<b>Выберите действие:</b>", reply_markup=markup_manage_event)

@dp.message_handler(Text(equals=["Показать"]), state=Back.Events)
async def show_all_events(message: types.Message):
    data_active = db.get_events({'event_status' : events.status.new})
    data_cancled = db.get_events({'event_status' : events.status.cancled})
    data_finish = db.get_events({'event_status' : events.status.finished})
    msg = "<b>Активные мероприятия:\n</b>"
    for i, obj in enumerate(data_active):
        msg += f"{i+1}. <code>{obj[0]}</code> : {obj[7]}\n"
    msg += "<b>\nОтменённые мероприятия:\n</b>"
    for i, obj in enumerate(data_cancled):
        msg += f"{i+1}. <code>{obj[0]}</code> : {obj[7]}\n"
    msg += "<b>\nЗавершённые мероприятия:\n</b>"
    for i, obj in enumerate(data_finish):
        msg += f"{i+1}. <code>{obj[0]}</code> : {obj[7]}\n"

    await message.answer(msg)

@dp.message_handler(Text(equals=["Удалить"]), state=Back.Events)
async def delete_event(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отменить")
            ],
        ],
        resize_keyboard=True,
    )
    await ManageEvent.event_cancel.set()
    await message.answer("Вставьте <i>id мероприятия</i>, которое вы хотите удалить", reply_markup=markup)

@dp.message_handler(Text(equals=["Завершить"]), state=Back.Events)
async def finish_event(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отменить")
            ],
        ],
        resize_keyboard=True,
    )
    await ManageEvent.event_finish.set()
    await message.answer("Вставьте <i>id мероприятия</i>, которое вы хотите завершить", reply_markup=markup)

@dp.message_handler(Text(equals=["Отменить"]), state=list(CreateEvent.states)+[Back.Events]+list(ManageEvent.states))
async def event_manage_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await Back.Events.set()
    await message.answer("<b>Выберите действие:</b>", reply_markup=markup_manage_event)

@dp.message_handler(state=list(ManageEvent.states))
async def handle_events(message: types.Message, state: FSMContext):
    logger.debug(f"Cancel or remove event {message.text}")
    r = -1
    if await state.get_state() == ManageEvent.event_finish.state:
        r = db.update_data_event(message.text, message.from_id, {"event_status": events.status.finished})
        if r > 0: await message.reply("Мероприятие успешно заврешено")
    else:
        r = db.update_data_event(message.text, message.from_id, {"event_status": events.status.cancled})
        if r > 0: await message.reply("Мероприятие успешно отменено")
    if r == -1: await message.reply("Невозможно выполнить операцию")
    if r == 0: await message.reply("Мероприятия с таким id <b>не существует</b>")
    await event_manage_cancel(message, state)


markup_create = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отменить")
        ],
    ],
    resize_keyboard=True,
)

@dp.message_handler(Text(equals=["Создать"]), state=Back.Events)
async def event_create(message: types.Message):
    await CreateEvent.title.set()
    await message.answer("<b>Введите название мероприятия:</b>", reply_markup=markup_create)

create_cb = CallbackData('create', 'key', 'value')

@dp.callback_query_handler(create_cb.filter(), state=list(CreateEvent.states))
async def process_create_event(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    key = callback_data.get('key')
    value = int(callback_data.get('value'))
    msg = ''
    if key == 'event_type': msg = events.type(value).description
    if key == 'start_time': msg = events.time(value).description
    if key == 'event_date': msg = events.date(value).description
    if key == 'duration': msg = events.duration(value).description

    current_state = None
    async with state.proxy() as data:
        data[key] = value
        current_state = data.state
    if current_state == CreateEvent.event_type.state:
        await call.message.edit_text(f"Тип мероприятия: {msg}", reply_markup=None)
        await event_create_time(call.message)
    if current_state == CreateEvent.start_time.state:
        await call.message.edit_text(f"Время начала: {msg}", reply_markup=None)
        await event_create_date(call.message)
    if current_state == CreateEvent.event_date.state:
        await call.message.edit_text(f"Дата начала: {msg}", reply_markup=None)
        await event_create_duration(call.message)
    if current_state == CreateEvent.duration.state:
        await call.message.edit_text(f"Продолжительность: {msg}", reply_markup=None)
        await call.message.answer("Введите имя организатора:")
        await CreateEvent.next()

@dp.message_handler(state=CreateEvent.title)
async def event_create_title(message: types.Message, state: FSMContext):
    logger.debug(f"Title: {message.text}")
    async with state.proxy() as data:
        data["title"] = message.text
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.type.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=create_cb.new(key='event_type', value=obj.value)))
    await message.answer("Выберите тип мероприятия:", reply_markup=options)
    await CreateEvent.next()

@dp.message_handler(state=CreateEvent.event_type)
async def event_create_time(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.time.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=create_cb.new(key='start_time', value=obj.value)))
    await message.answer("Выберите время начала:", reply_markup=options)
    await CreateEvent.next()

@dp.message_handler(state=CreateEvent.start_time)
async def event_create_date(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.date.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=create_cb.new(key='event_date', value=obj.value)))
    await message.answer("Выберите дату начала:", reply_markup=options)
    await CreateEvent.next()

@dp.message_handler(state=CreateEvent.event_date)
async def event_create_duration(message: types.Message):
    options = InlineKeyboardMarkup(row_width=1)
    for obj in events.duration.__members__.values():
        options.add(InlineKeyboardButton(obj.description, callback_data=create_cb.new(key='duration', value=obj.value)))
    await message.answer("Выберите продолжительность:", reply_markup=options)
    await CreateEvent.next()

@dp.message_handler(state=CreateEvent.organization)
async def event_create_org(message: types.Message, state: FSMContext):
    logger.debug(f"Organization: {message.text}")
    data = await state.get_data()
    data['organization'] = message.text
    r = db.insert_data_event([events.status.new.value, message.from_id, message.from_user.username] + list(data.values()))
    if r: await message.answer("Мероприятие успешно создано")
    else: await message.answer("<b>Произошла ошибка во время создания мероприятия</b>")
    await event_manage_cancel(message, state)

def start():
    logger.debug(f"Bot has been started")
    executor.start_polling(dp, skip_updates=True)