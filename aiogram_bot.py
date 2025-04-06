import asyncio
import logging
import sqlite3
from os import getenv

from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder as RKB
from aiogram.utils.keyboard import InlineKeyboardBuilder as IKB
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

TOKEN = 'TOKEN'  # Рекомендуется использовать переменные окружения

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    phonenumber = State()
    mail = State()
    teleid = State()
    address = State()

@dp.callback_query(F.data)
async def callback(call: types.CallbackQuery):
    if call.data == 'согласие':
        try:
            con = sqlite3.connect('userdata.db')
            cur = con.cursor()
            cur.execute("INSERT INTO user (name, pnumber, mail, address, teleid) VALUES (?, ?, ?, ?, ?)", 
                        (data["name"], data['phonenumber'], data['mail'], data['address'], data['teleid']))
            con.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных: {e}")
        finally:
            con.close()  # Закрываем соединение
        await bot.delete_message(call.message.chat.id, srmsgid)
        await call.message.answer("Вы зарегистрированы!")
    if call.data == 'отказ':
        await call.message.answer("Извините, вы не можете создать аккаунт без соглашения.")
        await bot.delete_message(call.message.chat.id, srmsgid)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(message.text)
    builder = RKB()
    regbutton = types.KeyboardButton(text="Регистрация")
    builder.add(regbutton)
    await message.reply(f"Привет, {html.bold(message.from_user.full_name)}! Чтобы получить помощь с решением проблемы тебе нужно зарегистрироваться!")
    await message.reply("Для регистрации нажмите кнопку ниже:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.startswith('Регистрация'))
async def startreg(message:Message, state: FSMContext) -> None:
    await message.answer("Введите своё ФИО:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

@dp.message(F.text, Form.name)
async def reg1(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.reply("Напишите свой номер телефона:")
    await state.set_state(Form.phonenumber)

@dp.message(F.text, Form.phonenumber)
async def reg2(message: Message, state: FSMContext) -> None:
    await state.update_data(phonenumber=message.text)
    await message.reply("Теперь введите свою почту ниже")
    await state.set_state(Form.mail)

@dp.message(F.text, Form.mail)
async def reg3(message: Message, state: FSMContext) -> None:
    await state.update_data(mail=message.text)
    await message.reply("Напишите адрес дома или квартиры")
    await state.set_state(Form.address)

@dp.message(F.text, Form.address)
async def reg4(message: Message, state: FSMContext) -> None:
    await state.update_data(teleid=message.from_user.id)
    await state.update_data(address=message.text)
    global data
    data = await state.get_data()

    builder = IKB()
    success = types.InlineKeyboardButton(text="Согласен", callback_data='согласие')
    reject = types.InlineKeyboardButton(text="Отказываюсь", callback_data='отказ')
    builder.add(success,reject)

    name = data["name"]
    phn = data["phonenumber"]
    mail = data["mail"]
    address = data["address"]

    srmsg = await message.answer(f"ФИО:{name}\nНомер телефона:{phn}\nЭлектронная почта:{mail}\nАдрес:{address}\n\nВы согласны на обработку персональных данных?", reply_markup=builder.as_markup())
    global srmsgid
    srmsgid = srmsg.message_id

async def main() -> None:
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
