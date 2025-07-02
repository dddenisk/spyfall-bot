import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command

import os
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Состояния FSM
class JoinState(StatesGroup):
    waiting_for_room = State()

# Хранилище комнат
rooms = {}

LOCATIONS = [
    "Аэропорт", "Больница", "Школа", "Университет", "Кафе", "Ресторан", "Метро", "Пляж", "Космическая станция",
    "Военная база", "Тюрьма", "Кемпинг", "Офис", "Свадьба", "Пиратский корабль", "Подводная лодка", "Цирк",
    "Театр", "Кинотеатр", "Музей", "Зоопарк", "Церковь", "Супермаркет", "Банк", "Стадион", "Ферма", "Парк",
    "Пожарная станция", "Полиция", "Автобус", "Поезд", "Трамвай", "Спа-салон", "Казино", "Гостиница", "Кладбище",
    "Гараж", "Прачечная", "Суд", "Кабинет психолога", "Морской порт", "Горнолыжный курорт", "Секретная лаборатория",
    "Частный дом", "Башня", "Обсерватория", "Книжный магазин", "Планетарий", "Арт-галерея", "Тату-салон", "Бар"
]

@dp.message(Command("start"))
async def start_handler(message: Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="Создать игру")
    kb.button(text="Присоединиться к игре")
    await message.answer("Привет! Что хотите сделать?", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message(F.text == "Создать игру")
async def create_game(message: Message):
    room_id = str(random.randint(1000, 9999))
    rooms[room_id] = {"owner": message.from_user.id, "players": {message.from_user.id: message.from_user.full_name}}
    await message.answer(f"Игра создана! Код комнаты: <b>{room_id}</b>\nПоделитесь им с друзьями.")

@dp.message(F.text == "Присоединиться к игре")
async def join_request(message: Message, state: FSMContext):
    await message.answer("Введите код комнаты:")
    await state.set_state(JoinState.waiting_for_room)

@dp.message(JoinState.waiting_for_room, F.text.regexp(r"^\d{4}$"))
async def join_game(message: Message, state: FSMContext):
    room_id = message.text
    if room_id in rooms:
        rooms[room_id]["players"][message.from_user.id] = message.from_user.full_name
        await message.answer(f"Вы присоединились к комнате {room_id}. Ожидайте начала игры.")
        await state.clear()
    else:
        await message.answer("Комната не найдена. Проверьте код.")

@dp.message(Command("начать"))
async def start_game(message: Message):
    for room_id, data in rooms.items():
        if data["owner"] == message.from_user.id:
            players = list(data["players"].items())
            if len(players) < 3:
                await message.answer("Минимум 3 игрока для начала игры.")
                return
            spy_id = random.choice(players)[0]
            location = random.choice(LOCATIONS)
            for user_id, name in players:
                if user_id == spy_id:
                    await bot.send_message(user_id, "Ты ШПИОН! Попробуй угадать локацию.")
                else:
                    await bot.send_message(user_id, f"Ты не шпион. Локация: <b>{location}</b>")
            await message.answer("Роли розданы. Начинайте обсуждение!")
            del rooms[room_id]
            return
    await message.answer("Вы не создавали игру или она уже завершена.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
