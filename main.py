import os
import asyncio

import psycopg2

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
import aiohttp

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


def dbConnect():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='tgbot',
        user='tgbotadmin',
        password='321')

    return conn


def dbClose(cursor, connection):
    cursor.close()
    connection.close()


async def send_post_request(url, json_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data) as response:
            data = await response.json()
            return data


async def send_get_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


kb = [
    [types.KeyboardButton(text='Добавить валюту')],
    [types.KeyboardButton(text='Удалить валюту')],
    [types.KeyboardButton(text='Изменить курс валюты')]
]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

url = 'http://127.0.0.1:5003/check_admin'


class states(StatesGroup):
    add_name = State()
    add_rate = State()
    del_name = State()
    edit_name = State()
    edit_rate = State()
    convert_name = State()
    convert_rate = State()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        'Привет, я DeepBot.'
    )


@dp.message(Command('manage_currency'))
async def manage_currency(message: types.Message):
    id = message.chat.id
    response_data = await send_post_request(url, {'id': id})
    if 'error' in response_data:
        await message.answer('Нет доступа.')
        return
    else:
        await message.answer('Выберите действие.', reply_markup=keyboard)


@dp.message(F.text == 'Добавить валюту')
async def add_name(message: types.Message, state: FSMContext):
    id = message.chat.id
    response_data = await send_post_request(url, {'id': id})
    if 'error' in response_data:
        await message.answer('Нет доступа.')
        return
    else:
        await message.answer('Введите название валюты.')
        await state.set_state(states.add_name)


@dp.message(states.add_name)
async def add_rate(message: types.Message, state: FSMContext):
    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f'SELECT currency_name FROM currencies WHERE currency_name = %s;', (message.text.strip().upper(),))

    if cur.fetchone():
        await message.answer('Данная валюта уже существует.')
        await state.set_state(None)
        return

    dbClose(cur, conn)

    await state.update_data(name=message.text)
    await message.answer('Введите курс рубля к единице данной валюты.')

    await state.set_state(states.add_rate)


@dp.message(states.add_rate)
async def add_currency(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')

    url = 'http://127.0.0.1:5001/load'
    json_data = {'name': name, 'rate': message.text}
    response_data = await send_post_request(url, json_data)

    if 'error' in response_data:
        await message.answer(str(response_data['error']))
    else:
        await message.answer(str(response_data['message']))

    await state.set_state(None)


@dp.message(F.text == 'Удалить валюту')
async def del_name(message: types.Message, state: FSMContext):
    id = message.chat.id
    response_data = await send_post_request(url, {'id': id})
    if 'error' in response_data:
        await message.answer('Нет доступа.')
        return
    else:
        await message.answer('Введите название валюты.')
        await state.set_state(states.del_name)


@dp.message(states.del_name)
async def del_currency(message: types.Message, state: FSMContext):
    url = 'http://127.0.0.1:5001/delete'
    json_data = {'name': message.text.upper().strip()}
    response_data = await send_post_request(url, json_data)

    if 'error' in response_data:
        await message.answer(str(response_data['error']))
    else:
        await message.answer(str(response_data['message']))

    await state.set_state(None)


@dp.message(F.text == 'Изменить курс валюты')
async def edit_name(message: types.Message, state: FSMContext):
    id = message.chat.id
    response_data = await send_post_request(url, {'id': id})
    if 'error' in response_data:
        await message.answer('Нет доступа.')
        return
    else:
        await message.answer('Введите название валюты.')
        await state.set_state(states.edit_name)


@dp.message(states.edit_name)
async def edit_rate(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите курс рубля к единице данной валюты.')

    await state.set_state(states.edit_rate)


@dp.message(states.edit_rate)
async def edit_currency(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')

    url = 'http://127.0.0.1:5001/update_currency'
    json_data = {'name': name, 'rate': message.text}
    response_data = await send_post_request(url, json_data)

    if 'error' in response_data:
        await message.answer(str(response_data['error']))
    else:
        await message.answer(str(response_data['message']))

    await state.set_state(None)


@dp.message(Command('get_currencies'))
async def get_currencies(message: types.Message):
    url = 'http://127.0.0.1:5002/currencies'
    response_data = await send_get_request(url)

    currencies = response_data.get('currencies')
    message_text = "Список валют:\n"
    for currency in currencies:
        currency_name = currency.get('currency_name')
        rate = currency.get('rate')
        message_text += f"Валюта: {currency_name}, Курс: {rate}\n"
    await message.answer(message_text)


@dp.message(Command('convert'))
async def convert_name(message: types.Message, state: FSMContext):
    await message.answer('Введите название валюты.')
    await state.set_state(states.convert_name)


@dp.message(states.convert_name)
async def convert_rate(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите сумму.')
    await state.set_state(states.convert_rate)


@dp.message(states.convert_rate)
async def convert_currency(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')

    url = 'http://127.0.0.1:5002/convert?currency_name=' + name + '&amount=' + message.text
    response_data = await send_get_request(url)

    if 'error' in response_data:
        await message.answer(str(response_data['error']))
    else:
        await message.answer(str(response_data['converted_amount']))

    await state.set_state(None)


@dp.message()
async def any_commands(message: types.Message):
    await message.answer('Такой команды нет, мне нечего ответить.')

comands = [
    BotCommand(command='/start', description='Начать работу'),
    BotCommand(command='/manage_currency', description='Управление'),
    BotCommand(command='/get_currencies', description='Все валюты'),
    BotCommand(command='/convert', description='Конвертировать'),
]


async def main():
    await bot.set_my_commands(comands, scope=BotCommandScopeDefault())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
