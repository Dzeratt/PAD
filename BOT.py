import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import *

import logging

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class Variables(StatesGroup):
    currency_name = State()
    currency_rate = State()
    convert_number = State()
    converting = State()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer('Привет, я DeepBot. Чтобы конвертировать валюты используй /currency_rate')


@dp.message(Command('currency_rate'))
async def get_currency_rate(message: types.Message, state: FSMContext):
    await message.answer('Введите название валюты:')
    await state.set_state(Variables.currency_name)


@dp.message(Variables.currency_name)
async def save_currency_name(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer("Пожалуйста, введите не цифрами")
        return
    await state.update_data(currency_name=message.text)
    await message.answer("Введите курс рубля к единице валюты:")
    await state.set_state(Variables.currency_rate)


@dp.message(Variables.currency_rate)
async def save_convert_number(message: types.Message, state: FSMContext):
    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно  ЧИСЛО для конвертации в рубли")
        return
    convert_number = float(message.text)
    if convert_number <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО для конвертации в рубли.")
        return
    await state.update_data(currency_rate=message.text)
    await message.answer("Введите сумму, которую хотите конвертировать в рубли:")
    await state.set_state(Variables.convert_number)


@dp.message(Variables.convert_number)
async def converting(message: types.Message, state: FSMContext):
    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно  ЧИСЛО для конвертации в рубли")
        return
    convert_number = float(message.text)
    if convert_number <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО для конвертации в рубли.")
        return
    await state.update_data(convert_number=message.text)
    converting_data = await state.get_data()
    currency_name = converting_data.get("currency_name")
    currency_rate = converting_data.get("currency_rate")
    await message.answer(f"Информация для конвертации:\n"
                         f"Название валюты: {currency_name}\n"
                         f"Курс валюты к 1 рублю: {currency_rate}\n"
                         f"Сумма для конвертации: {message.text}\n"
                         f"Сумма в рублях: {float(message.text) * float(currency_rate)}")
    await state.set_state(Variables.converting)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
