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


currency_rates = {}


class Variables(StatesGroup):
    currency_name = State()
    currency_rate = State()
    convert_name = State()
    convert_number = State()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f'Привет, я DeepBot\n'
        f'Чтобы сохранить валюту используй /save_currency\n'
        f'Чтобы конвертировать валюту используй /convert\n'
    )


@dp.message(Command('save_currency'))
async def get_currency_name(message: types.Message, state: FSMContext):
    await message.answer('Введите название валюты:')
    await state.set_state(Variables.currency_name)


@dp.message(Variables.currency_name)
async def get_currency_rate(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer("Пожалуйста, введите буквами")
        return
    await state.update_data(currency_name=message.text)
    await message.answer("Введите курс рубля к единице валюты:")
    await state.set_state(Variables.currency_rate)


@dp.message(Variables.currency_rate)
async def save_currency_data(message: types.Message, state: FSMContext):
    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно ЧИСЛО для конвертации в рубли")
        return
    convert_rate = float(message.text)
    if convert_rate <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО для конвертации в рубли.")
        return
    converting_data = await state.get_data()
    currency_name = converting_data.get("currency_name")
    currency_rates[currency_name] = convert_rate
    await state.update_data(currency_rate=convert_rate)
    await message.answer(
        f"Валюта '{currency_name}' сохранена с курсом {convert_rate} к 1 рублю."
        f'Вы можете сохранить еще одну валюту (/save_currency) или конвертировать уже имеющиеся (/convert)'
    )
    await state.set_state(None)


@dp.message(Command('convert'))
async def get_convert_name(message: types.Message, state: FSMContext):
    if not currency_rates:
        await message.answer("Нет сохраненных валют. Сначала сохраните валюту командой /save_currency")
        return
    await message.answer("Введите название валюты для конвертации:")
    response_message = "Доступные для конвертации валюты и их курсы к рублю:\n"
    for currency_name, rate in currency_rates.items():
        response_message += f"{currency_name}: {rate}\n"
    await message.answer(response_message)
    await state.set_state(Variables.convert_name)


@dp.message(Variables.convert_name)
async def get_convert_number(message: types.Message, state: FSMContext):
    currency_name = message.text
    if currency_name not in currency_rates:
        await message.answer(f"Валюта '{currency_name}' не найдена в словаре.")
        return

    await state.update_data(convert_currency=currency_name)
    await message.answer(f"Вы выбрали валюту '{currency_name}'. Введите сумму для конвертации в рубли:")
    await state.set_state(Variables.convert_number)


@dp.message(Variables.convert_number)
async def finish_conversion(message: types.Message, state: FSMContext):
    converting_data = await state.get_data()
    convert_currency = converting_data.get("convert_currency")  # Use correct key
    if convert_currency not in currency_rates:
        await message.answer(f"Валюта '{convert_currency}' не найдена в словаре.")
        return

    convert_number = float(message.text)
    converted_amount = convert_number * currency_rates[convert_currency]

    await message.answer(f"Результат конвертации:\n"
                         f"{convert_number} {convert_currency} = {converted_amount} рублей")

    await state.set_state(None)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
