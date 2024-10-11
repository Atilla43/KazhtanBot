from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio

from aiogram.filters import CommandStart

# Добавляем кнопки
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram import F # Импортируем Magic Filter

# Так мы не делаем
# from aiogram.utils.executor import start_polling # Изменено!

# import io
import logging as lg
import sqlite3
# import os
# from PIL import Image

# Токен
TOKEN = "token"
ADMIN_ID="590317122"


# Имя файла базы данных
DB_FILE = "users.db"

# Создаем объект бота
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Класс состояний для обработки запроса
class UserForm(StatesGroup):
  fio = State()
  adults = State()
  children = State()
  payment_receipt = State()
  transfer = State()

# Создание таблицы в базе данных
def create_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fio TEXT,
      adults INTEGER,
      children INTEGER,
      payment_receipt BLOB,
      transfer TEXT
    )
  """)
  conn.commit()
  conn.close()

# Сохранение информации в базу данных
async def save_to_db(user_id, fio, adults, children, payment_receipt, transfer):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
    "INSERT INTO users (fio, adults, children, payment_receipt, transfer) VALUES (?, ?, ?, ?, ?)",
    (fio, adults, children, str(payment_receipt), transfer),
  )
  conn.commit()
  conn.close()

# Отправка информации администратору
async def send_to_admin(user_id, fio, adults, children, payment_receipt, transfer):
  # Заменяем BLOB-данные фотографией
  # img = Image.open(io.BytesIO(payment_receipt)))
  # img.save("payment_receipt.jpg")

  # Формируем текст сообщения
  '''
  о ужас, мои глаза...
  message = f"Новый запрос от пользователя {user_id}:\n\n"
  message += f"ФИО: {fio}\n"
  message += f"Взрослые: {adults}\n"
  message += f"Дети: {children}\n"
  message += f"Трансфер: {transfer}\n"
  '''
  message = f"""
  Новый запрос от пользователя {user_id}:

    ФИО: {fio}
    Взрослые: {adults}
    Дети: {children}
    Трансфер: {transfer}
  """

  # Отправка сообщения с фотографией
  await bot.send_photo(
    chat_id=ADMIN_ID,
    photo=payment_receipt,
    caption=message,
  )
  await bot.send_photo(
    chat_id=590317122,
    photo=payment_receipt,
    caption=message,
  )

  # Удаление временного файла
  # os.remove("payment_receipt.jpg")

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
  await message.answer(
    "Привет!👋\n"
    "Чтобы оформить бронь, пожалуйста, отправьте свои данные.\n"
    "Начнём с вашего ФИО."
  )
  await state.set_state(UserForm.fio)

# Обработчик ввода ФИО

# Так не нада
# @dp.message_handler(state=UserForm.fio)
# Нада вот так
@dp.message(UserForm.fio)
async def fio_handler(message: types.Message, state: FSMContext):
  # Так не нада
  # async with state.proxy() as data:
  # Нада вот так
  await state.update_data(fio=message.text)

  await message.answer("Сколько взрослых будет ехать?")
  # await UserForm.adults.set() Так не нада
  await state.set_state(UserForm.adults) # Нада вот так

# Обработчик ввода количества взрослых
# @dp.message_handler(state=UserForm.adults)
@dp.message(UserForm.adults)
async def adults_handler(message: types.Message, state: FSMContext):
  try:
    adults = int(message.text)
    await state.update_data(adults=adults)
    await message.answer("Сколько детей будет ехать?")
    await state.set_state(UserForm.children)
  except ValueError:
    await message.answer("Пожалуйста, введите число.")

# Обработчик ввода количества детей
@dp.message(UserForm.children)
async def children_handler(message: types.Message, state: FSMContext):
  try:
    children = int(message.text)
    data = await state.get_data()
    await state.update_data(children=children)
    await message.answer(
      "Отправьте фотографию чека об оплате."
    )
    await state.set_state(UserForm.payment_receipt)
  except ValueError:
    await message.answer("Пожалуйста, введите число.")

# Обработчик ввода фотографии чека
@dp.message(F.photo, UserForm.payment_receipt)
async def payment_receipt_handler(message: types.Message, state: FSMContext):
  data = await state.get_data()

  file_id = message.photo[-1].file_id
  file = await bot.get_file(file_id)
  # file_path = file.file_path
  # У каждого файла есть свой уникальный ID
  # Его можно запоминать и присылать админу не скачивая его
  # await message.answer_photo(<photo_id>)
          #  await bot.download_file(file_path)
  await state.update_data(payment_receipt = file_id)

  keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
      [
        InlineKeyboardButton(text="Да", callback_data="transfer_yes"),
        InlineKeyboardButton(text="Нет", callback_data="transfer_no"),
      ]
    ]
  )
  await message.answer(
    "Нужен ли трансфер от Медвежьего угла до Медовеевки?", reply_markup=keyboard
  )
  await state.set_state(UserForm.transfer)

# Обработчик кнопки "Да" для трансфера

# так не нада
# @dp.callback_query_handler(text="transfer_yes", state=UserForm.transfer)
# Нада вот так
@dp.callback_query(F.data=="transfer_yes", UserForm.transfer)
async def transfer_yes_handler(call: types.CallbackQuery, state: FSMContext):
  await call.message.answer("Трансфер нужен.")
  data = await state.get_data()
  data["transfer"] = "Да"
  await save_to_db(
    "@"+call.from_user.username,
    data["fio"],
    data["adults"],
    data["children"],
    data["payment_receipt"],
    data["transfer"],
  )
  await send_to_admin(
    "@"+call.from_user.username,
    data["fio"],
    data["adults"],
    data["children"],
    data["payment_receipt"],
    data["transfer"],
  )
  await call.message.answer("Запрос отправлен администратору.")
  await state.clear()

# Обработчик кнопки "Нет" для трансфера
@dp.callback_query(F.data=="transfer_no", UserForm.transfer)
async def transfer_no_handler(call: types.CallbackQuery, state: FSMContext):
  await call.message.answer("Трансфер не нужен.")
  data = await state.get_data()
  data["transfer"] = "Нет"
  await save_to_db(
    "@"+call.from_user.username,
    data["fio"],
    data["adults"],
    data["children"],
    data["payment_receipt"],
    data["transfer"],
  )
  await send_to_admin(
    "@"+call.from_user.username,
    data["fio"],
    data["adults"],
    data["children"],
    data["payment_receipt"],
    data["transfer"],
  )
  await call.message.answer("Запрос отправлен администратору.")
  await state.clear()


async def main():
  # Инициируем logger для информирования
  lg.basicConfig(level=lg.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(asctime)s -  %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )

  await dp.start_polling(bot, skip_updates=True) # Используйте start_polling

# Запуск бота
if __name__ == "__main__":
  create_db()
  asyncio.run(main())
