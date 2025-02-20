import asyncio, logging, sys
import sqlite3
from os import getenv

from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder as RKB

TOKEN = "7409950736:AAFDXEFVIsn0Dp0pCYyK66ooQ0SOTK6iW3U"

dp = Dispatcher()
class form(StatesGroup):
    name = State()
    phonenumber = State()
    mail = State()
    address = State()

@dp.message(F.text)
async def command_start_handler(message:Message) -> None:
    if message.text == "/start":
        builder = RKB()
        regbutton = types.KeyboardButton(text="Создать запрос")
        builder.add(regbutton)
        await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!")
        await message.answer("Для создания запроса нажмите кнопку ниже:", reply_markup=builder.as_markup())
    if message.text == 'Создать запрос':
        await regname(message, FSMContext)

@dp.message(form.name)
async def regname(message:Message, state: FSMContext) -> None:
    await message.answer("Введите своё ФИО:")
    await state.set_state(form.name)
    await state.update_data(name=message.text)

@dp.message(form.phonenumber)
async def regphonenum(message:Message, state: FSMContext) -> None:
    await message.answer("Напишите свой номер телефона:")
    await state.set_state(form.phonenumber)
    await state.update_data(phonenumber=message.text)

@dp.message(form.mail, F.text)
async def regmail(message:Message, state: FSMContext) -> None:
    await message.answer("Теперь введите свою почту ниже:")
    await state.set_state(form.mail)
    await state.update_data(mail=message.text)

@dp.message(form.address, F.text)
async def regadress(message:Message, state: FSMContext) -> None:
    await message.answer("Напишите адрес дома или квартиры:")
    await state.set_state(form.address)
    await state.update_data(address=message.text)

    try:
        con = sqlite3.connect('userdata.db')
        cur = con.cursor()
        cur.execute(f"""
        INSERT INTO user VALUES
        ('{form.name}, {form.phonenumber}, {form.mail}, {form.address}')
        """)
    except Exception:
        print("Ошибочка")
    
#@dp.message(form.name)
#async def process_name(message:Message, state:FSMContext) -> None:

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())