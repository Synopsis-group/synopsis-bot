'''from aiogram import Dispatcher, Bot, executor
from aiogram import types
import logging

from synopsis.db.database import DataBase
from synopsis.config.settings import settings
from synopsis.config.users import users

# Константы для обработки кнопок
BUTTON_VREMYA = 'Время начала'
BUTTON_DATA = 'Дата начала'
BUTTON_DURATION = 'Продолжительность'
BUTTON_ORGANIZATION = 'Организация'
BUTTON_RESET = 'Сбросить'
BUTTON_BACK = 'Назад'
BUTTON_SHOW_NUM = 'Показать num'
BUTTON_TYPE = 'Тип мероприятия'

BUTTON_VREMYA_DO12 = 'До 12'
BUTTON_VREMYA_12TO18 = 'С 12 до 18'
BUTTON_VREMYA_16TO19 = 'С 16 до 19'
BUTTON_VREMYA_POZNEE19 = 'Позднее 19'

BUTTON_DATA_SEGODNYA = 'Сегодня'
BUTTON_DATA_ZAVTRA = 'Завтра'
BUTTON_DATA_NEDELYA = 'Ближайшая неделя'

BUTTON_DURATION_30 = '~30'
BUTTON_DURATION_1H = '~1:00'
BUTTON_DURATION_1H30M = '~1:30'
BUTTON_DURATION_2H = '~2:00'
BUTTON_DURATION_2H30M = '~2:30'
BUTTON_DURATION_3H = '~3:00'
BUTTON_DURATION_MORE_THAN_3H = 'Более 3 ч'

BUTTON_ORGANIZATION_SYUT = 'СЮТ'
BUTTON_ORGANIZATION_NEYVA = 'НЕЙВА'
BUTTON_ORGANIZATION_DYUSH = 'ДЮСШ'

BUTTON_TYPE_SPORT = 'Спорт'
BUTTON_TYPE_EDUCATION = 'Образование'
BUTTON_TYPE_CULTURE = 'Культура'

logger = logging.getLogger('logger')

# Словарь для хранения выбранных параметров
params = {}

bot = Bot(token=settings.bots.token)
dp = Dispatcher(bot)
db = None

# Хендлер для команды /start (запуск бота)
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Стартовое сообщение от бота
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_VREMYA, BUTTON_DATA)
    markup.row(BUTTON_DURATION, BUTTON_ORGANIZATION)
    markup.row(BUTTON_SHOW_NUM, BUTTON_TYPE)
    markup.row(BUTTON_RESET)

    await message.reply("Привет! Я помогу тебе найти интересующее тебя мероприятие. Выбери параметры поиска:", reply_markup=markup)

# Хендлер для кнопок
@dp.message_handler(lambda message: message.text in [BUTTON_VREMYA, BUTTON_DATA, BUTTON_DURATION, BUTTON_ORGANIZATION, BUTTON_TYPE])
async def handle_buttons(message: types.Message):
    # Обнуляем словарь parameters при начале нового поиска
    if message.text != BUTTON_BACK:
        params.clear()

    # Проверяем на какую кнопку нажал пользователь и выводим соответствующие кнопки
    if message.text == BUTTON_VREMYA:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BUTTON_VREMYA_DO12, BUTTON_VREMYA_12TO18)
        markup.row(BUTTON_VREMYA_16TO19, BUTTON_VREMYA_POZNEE19)
        markup.row(BUTTON_BACK)
        await message.reply("Выбери время начала мероприятия:", reply_markup=markup)
    elif message.text == BUTTON_DATA:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BUTTON_DATA_SEGODNYA, BUTTON_DATA_ZAVTRA)
        markup.row(BUTTON_DATA_NEDELYA, BUTTON_BACK)
        await message.reply("Выбери дату начала мероприятия:", reply_markup=markup)
    elif message.text == BUTTON_DURATION:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BUTTON_DURATION_30, BUTTON_DURATION_1H, BUTTON_DURATION_1H30M)
        markup.row(BUTTON_DURATION_2H, BUTTON_DURATION_2H30M, BUTTON_DURATION_3H)
        markup.row(BUTTON_DURATION_MORE_THAN_3H, BUTTON_BACK)
        await message.reply("Выбери продолжительность мероприятия:", reply_markup=markup)
    elif message.text == BUTTON_ORGANIZATION:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BUTTON_ORGANIZATION_SYUT, BUTTON_ORGANIZATION_NEYVA)
        markup.row(BUTTON_ORGANIZATION_DYUSH, BUTTON_BACK)
        await message.reply("Выбери организацию:", reply_markup=markup)
    elif message.text == BUTTON_SHOW_NUM:
        await message.reply("Здесь будет отображаться число найденных мероприятий. Для продолжения поиска выбери параметры поиска ")
    elif message.text == BUTTON_TYPE:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BUTTON_TYPE_SPORT, BUTTON_TYPE_EDUCATION)
        markup.row(BUTTON_TYPE_CULTURE)
        markup.row(BUTTON_BACK)
        await message.reply("Выбери тип мероприятия:", reply_markup=markup)

# Хендлер для кнопок выбора времени начала мероприятия
@dp.message_handler(lambda message: message.text in [BUTTON_VREMYA_DO12, BUTTON_VREMYA_12TO18, BUTTON_VREMYA_16TO19, BUTTON_VREMYA_POZNEE19])
async def handle_button_vremya(message: types.Message):
    if message.text == BUTTON_VREMYA_DO12:
        params['vremya'] = 'Do12'
    elif message.text == BUTTON_VREMYA_12TO18:
        params['vremya'] = '12To18'
    elif message.text == BUTTON_VREMYA_16TO19:
        params['vremya'] = '16To19'
    elif message.text == BUTTON_VREMYA_POZNEE19:
        params['vremya'] = 'Poznee19'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_BACK)
    await message.reply("Выбрано время начала мероприятия: " + message.text, reply_markup=markup)

# Хендлер для кнопок выбора даты начала мероприятия
@dp.message_handler(lambda message: message.text in [BUTTON_DATA_SEGODNYA, BUTTON_DATA_ZAVTRA, BUTTON_DATA_NEDELYA])
async def handle_button_data(message: types.Message):
    if message.text == BUTTON_DATA_SEGODNYA:
        params['data'] = 'Segodnya'
    elif message.text == BUTTON_DATA_ZAVTRA:
        params['data'] = 'Zavtra'
    elif message.text == BUTTON_DATA_NEDELYA:
        params['data'] = 'Nedelya'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_BACK)
    await message.reply("Выбрана дата начала мероприятия: " + message.text, reply_markup=markup)

# Хендлер для кнопок выбора продолжительности мероприятия
@dp.message_handler(lambda message: message.text in [BUTTON_DURATION_30, BUTTON_DURATION_1H, BUTTON_DURATION_1H30M, BUTTON_DURATION_2H, BUTTON_DURATION_2H30M, BUTTON_DURATION_3H, BUTTON_DURATION_MORE_THAN_3H])
async def handle_button_duration(message: types.Message):
    if message.text == BUTTON_DURATION_30:
        params['duration'] = '~30'
    elif message.text == BUTTON_DURATION_1H:
        params['duration'] = '~1:00'
    elif message.text == BUTTON_DURATION_1H30M:
        params['duration'] = '~1:30'
    elif message.text == BUTTON_DURATION_2H:
        params['duration'] = '~2:00'
    elif message.text == BUTTON_DURATION_2H30M:
        params['duration'] = '~2:30'
    elif message.text == BUTTON_DURATION_3H:
        params['duration'] = '~3:00'
    elif message.text == BUTTON_DURATION_MORE_THAN_3H:
        params['duration'] = 'MoreThan3'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_BACK)
    await message.reply("Выбрана продолжительность мероприятия: " + message.text, reply_markup=markup)

# Хендлер для кнопок выбора организации
@dp.message_handler(lambda message: message.text in [BUTTON_ORGANIZATION_SYUT, BUTTON_ORGANIZATION_NEYVA, BUTTON_ORGANIZATION_DYUSH])
async def handle_button_organization(message: types.Message):
    if message.text == BUTTON_ORGANIZATION_SYUT:
        params['organization'] = 'SYUT'
    elif message.text == BUTTON_ORGANIZATION_NEYVA:
        params['organization'] = 'NEYVA'
    elif message.text == BUTTON_ORGANIZATION_DYUSH:
        params['organization'] = 'DYUSH'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_BACK)
    await message.reply("Выбрана организация: " + message.text, reply_markup=markup)

# Хендлер для кнопок выбора типа мероприятия
@dp.message_handler(lambda message: message.text in [BUTTON_TYPE_CULTURE, BUTTON_TYPE_EDUCATION, BUTTON_TYPE_SPORT, BUTTON_TYPE_SPORT])
async def handle_button_type(message: types.Message):
    if message.text == BUTTON_TYPE_CULTURE:
        params['type'] = 'culture'
    elif message.text == BUTTON_TYPE_EDUCATION:
        params['type'] = 'education'
    elif message.text == BUTTON_TYPE_SPORT:
        params['type'] = 'sport'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_BACK)
    await message.reply("Выбран тип мероприятия: " + message.text, reply_markup=markup)

# Хендлер для кнопки "Назад"
@dp.message_handler(lambda message: message.text == BUTTON_BACK)
async def handle_button_back(message: types.Message):
    # Если пользователь находился на этапе выбора параметров поиска
    if len(params) > 0:
        params.popitem()  # Удаляем последнюю выбранную пару ключ-значение
        await message.reply("Выбери параметры поиска:", reply_markup=get_search_markup())  # Возвращаемся на предыдущий шаг

# Хендлер для кнопки "Сбросить"
@dp.message_handler(lambda message: message.text == BUTTON_RESET)
async def handle_button_reset(message: types.Message):
    params.clear()  # Удаляем все выбранные параметры
    await message.reply("Выбери параметры поиска:", reply_markup=get_search_markup())  # Возвращаемся на начальный шаг

# Функция для получения текущей клавиатуры с выбранными параметрами
def get_search_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BUTTON_VREMYA + ' (' + str(params.get('vremya', '')) + ')')
    markup.row(BUTTON_DATA + ' (' + str(params.get('data', '')) + ')')
    markup.row(BUTTON_DURATION + ' (' + str(params.get('duration', '')) + ')')
    markup.row(BUTTON_ORGANIZATION + ' (' + str(params.get('organization', '')) + ')')
    markup.row(BUTTON_SHOW_NUM, BUTTON_TYPE + ' (' + str(params.get('type', '')) + ')')
    markup.row(BUTTON_RESET)
    return markup

def start(database: DataBase):
    db = database
    executor.start_polling(dp, skip_updates=True)'''

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

bot = Bot(token="6239875821:AAGERsKS6dk6wQM0vqIxSiwkomdk_R-VRN4")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class SearchEvents(StatesGroup):
    time_start = State()
    date_start = State()
    duration = State()
    organization = State()
    event_type = State()


def get_main_keyboard(user_type):
    if user_type == "admin":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поиск мероприятий"),
                    KeyboardButton(text="Управление событий"),
                ],
                [
                    KeyboardButton(text="Другое"),
                    KeyboardButton(text="Избранное"),
                ],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поиск мероприятий"),
                    KeyboardButton(text="Избранное"),
                ],
                [
                    KeyboardButton(text="Другое"),
                ],
            ],
            resize_keyboard=True,
        )


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_type = "user"
    # Проверяем, является ли пользователь админом
    if message.from_user.username in ["admin1", "admin2"]:
        user_type = "admin"

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


@dp.message_handler(Text(equals=["Другое"]))
async def other_handler(message: types.Message):
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


@dp.message_handler(Text(equals=["FAQ"]))
async def faq_handler(message: types.Message):
    await message.answer("Ссылка на FAQ: https://telegra.ph/FAQ-11-25")
    await cmd_start(message)


@dp.message_handler(Text(equals=["Настройки"]))
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

    await message.answer("Выберите настройку:", reply_markup=markup)


@dp.message_handler(Text(equals=["Город проживания"]))
async def choose_city(message: types.Message):
    cities = [
        "Новоуральск",
        "Москва",
        "Санкт-Петербург",
        "Новосибирск",
        "Екатеринбург",
        "Нижний Новгород",
        "Казань",
        "Самара",
        "Омск",
        "Челябинск",
        "Ростов-на-Дону",
    ]

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=city)] for city in cities
        ],
        resize_keyboard=True,
    )

    await message.answer("Выберите город:", reply_markup=markup)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)