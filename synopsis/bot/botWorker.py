from aiogram import Dispatcher, Bot, executor
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
    executor.start_polling(dp, skip_updates=True)
