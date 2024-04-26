import os
import asyncio

import psycopg2

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
import reply

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
        host="127.0.0.1",
        database="tgbot",
        user="tgbotadmin",
        password="321")

    return conn


def dbClose(cursor, connection):
    cursor.close()
    connection.close()


ADMIN_KB = reply.get_keyboard(
    "Добавить валюту",
    "Удалить валюту",
    "Изменить курс валюты",
    placeholder="Выберите действие",
    sizes=(3, 2, 1),
)


SEMI_ADMIN_KB = reply.get_keyboard(
    "/manage_currency",
    "/get_currencies",
    "/convert",
    "/start",
    placeholder="Выберите действие",
    sizes=(3, 1, 1),
)


USER_KB = reply.get_keyboard(
    "/get_currencies",
    "/convert",
    "/start",
    placeholder="Выберите действие",
    sizes=(3, 1, 1),
)


class Variables(StatesGroup):
    add_currency = State()
    add_rate = State()
    delete_currency = State()
    edit_currency = State()
    edit_rate = State()
    convert_name = State()
    convert_rate = State()
    check = State()


@dp.message(CommandStart())
async def start(message: types.Message):

    chat_id = message.chat.id

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM admins WHERE chat_id = '{chat_id}';")
    admin_id = cur.fetchone()

    if admin_id:
        await message.answer(f'Привет, я DeepBot\n', reply_markup=SEMI_ADMIN_KB)
    else:
        await message.answer(f'Привет, я DeepBot\n', reply_markup=USER_KB)

    dbClose(cur, conn)


@dp.message(Command('manage_currency'))
async def manage_currency(message: types.Message):

    chat_id = message.chat.id

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM admins WHERE chat_id = '{chat_id}';")
    admin_id = cur.fetchone()

    if admin_id:
        await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)
    else:
        await message.answer(f'Нет доступа')

    dbClose(cur, conn)


@dp.message(F.text == "Добавить валюту")
async def add_currency_first(message: types.Message, state: FSMContext):

    chat_id = message.chat.id

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM admins WHERE chat_id = '{chat_id}';")
    admin_id = cur.fetchone()

    if admin_id:
        await message.answer('Введите название валюты:')
    else:
        await message.answer(f'Нет доступа')

    dbClose(cur, conn)

    await state.set_state(Variables.add_currency)


@dp.message(Variables.add_currency)
async def add_currency_second(message: types.Message, state: FSMContext):

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT currency_name FROM currencies WHERE currency_name = '{message.text.strip().upper()}';")
    check_currency_name = cur.fetchone()

    if check_currency_name:
        await message.answer('Данная валюта уже существует')
        await state.set_state(None)
        return

    dbClose(cur, conn)

    await state.update_data(currency_name=message.text.strip().upper())

    await message.answer("Введите курс рубля к единице данной валюты:")

    await state.set_state(Variables.add_rate)


@dp.message(Variables.add_rate)
async def add_currency_third(message: types.Message, state: FSMContext):

    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно ЧИСЛО для конвертации в рубли")
        return

    rate = float(message.text)

    if rate <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО больше 0, для конвертации в рубли.")
        return

    currency_data = await state.get_data()
    currency_name = currency_data.get('currency_name')

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO currencies (currency_name, rate) VALUES ('{currency_name}', {rate});")
    conn.commit()

    await message.answer(f"Валюта: {currency_name} успешно добавлена")

    dbClose(cur, conn)

    await state.set_state(None)


@dp.message(F.text == "Удалить валюту")
async def del_currency_first(message: types.Message, state: FSMContext):

    chat_id = message.chat.id

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM admins WHERE chat_id = '{chat_id}';")
    admin_id = cur.fetchone()

    if admin_id:
        await message.answer('Введите название валюты:')
    else:
        await message.answer(f'Нет доступа')

    dbClose(cur, conn)

    await state.set_state(Variables.delete_currency)


@dp.message(Variables.delete_currency)
async def del_currency_second(message: types.Message, state: FSMContext):

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM currencies WHERE currency_name = '{message.text.strip().upper()}';")

    conn.commit()

    dbClose(cur, conn)

    await message.answer(f"Валюта: {message.text.strip().upper()} успешно удалена")

    await state.set_state(None)


@dp.message(F.text == "Изменить курс валюты")
async def edit_currency_first(message: types.Message, state: FSMContext):

    chat_id = message.chat.id

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM admins WHERE chat_id = '{chat_id}';")
    admin_id = cur.fetchone()

    if admin_id:
        await message.answer('Введите название валюты:')
    else:
        await message.answer(f'Нет доступа')

    await state.set_state(Variables.edit_currency)


@dp.message(Variables.edit_currency)
async def edit_currency_second(message: types.Message, state: FSMContext):
    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT currency_name FROM currencies WHERE currency_name = '{message.text.strip().upper()}';")
    check_currency_name = cur.fetchone()

    if not check_currency_name:
        await message.answer('Данная валюта не существует')
        await state.set_state(None)
        return

    dbClose(cur, conn)

    await state.update_data(currency_name=message.text.strip().upper())

    await message.answer("Введите курс рубля к единице данной валюты:")

    await state.set_state(Variables.edit_rate)


@dp.message(Variables.edit_rate)
async def edit_currency_third(message: types.Message, state: FSMContext):
    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно ЧИСЛО для конвертации в рубли")
        return

    rate = float(message.text)

    if rate <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО больше 0, для конвертации в рубли.")
        return

    currency_data = await state.get_data()
    currency_name = currency_data.get('currency_name')

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"UPDATE currencies SET rate = {rate} WHERE currency_name = '{currency_name}';")

    conn.commit()

    dbClose(cur, conn)

    await message.answer(f"Валюта: {currency_name} успешно изменена")

    await state.set_state(None)


@dp.message(Command('get_currencies'))
async def get_currencies(message: types.Message):

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name;")
    currencies = cur.fetchall()

    response = "Список валют и их курс:\n"

    for currency in currencies:
        currency_name, rate = currency
        response += f"{currency_name}: {float(rate)} руб.\n"

    dbClose(cur, conn)

    await message.answer(f"{response}")


@dp.message(Command('convert'))
async def convert_name(message: types.Message, state: FSMContext):

    await message.answer('Введите название валюты:')

    await state.set_state(Variables.convert_name)


@dp.message(Variables.convert_name)
async def convert_rate(message: types.Message, state: FSMContext):

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT currency_name FROM currencies WHERE currency_name = '{message.text.strip().upper()}';")
    check_convert_name = cur.fetchone()

    if not check_convert_name:
        await message.answer('Данная валюта не существует')
        await state.set_state(None)
        return

    dbClose(cur, conn)

    await state.update_data(currency_name=message.text.strip().upper())

    await message.answer("Введите количество валюты, которую хотите конвертировать:")

    await state.set_state(Variables.convert_rate)


@dp.message(Variables.convert_rate)
async def convert(message: types.Message, state: FSMContext):

    if not message.text.isnumeric() and not is_float(message.text):
        await message.answer("Пожалуйста, введите именно ЧИСЛО для конвертации в рубли")
        return

    rate = float(message.text)

    if rate <= 0:
        await message.answer("Пожалуйста, введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО больше 0, для конвертации в рубли.")

    currency_data = await state.get_data()
    currency_name = currency_data.get('currency_name')

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute(f"SELECT rate FROM currencies WHERE currency_name = '{currency_name}';")
    convert_rate = cur.fetchone()

    dbClose(cur, conn)

    convert_result = float(convert_rate[0]) * rate

    await message.answer(str(convert_result))

    await state.set_state(None)


async def main():
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
