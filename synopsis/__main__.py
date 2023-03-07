#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from aiogram import types, executor, Dispatcher, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


'''# log level
logging.basicConfig(level-logging.INFO)'''

# bot  init
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def begin(message:types.Message):
    markup = InlineKeyboardMarkup()
    but_1 = InlineKeyboardButton("Kek", callback_data="but_1")
    markup.add(but_1)

    await bot.send_message(message.chat.id, "Привет, Привет!", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "but_1")
async def button_reaction(call: types.callback_query):
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.message.chat.id, "чё кек то?")



executor.start_polling(dp)

if __name__ == '__main__':
    """Точка входа в программу.
    """
    print("hello")

