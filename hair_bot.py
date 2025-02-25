import asyncio
import logging
import random
import sqlite3
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# Включаем логирование
logging.basicConfig(level=logging.DEBUG)

# Токен бота
TOKEN = "7939519569:AAF_CHpFN22KtvyLnYiQR2iywcPDem6wdVU"

# Подключение к базе данных SQLite
conn = sqlite3.connect("hair_growth.db")
cursor = conn.cursor()

# Создаём таблицу для хранения длины волос
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        hair_length REAL DEFAULT 0.0,
        last_growth TEXT
    )
""")
conn.commit()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Функция получения топ-10 пользователей по длине волос
def get_top_users():
    cursor.execute("SELECT username, hair_length FROM users ORDER BY hair_length DESC LIMIT 10")
    top_users = cursor.fetchall()
    return top_users

# Функция проверки возможности роста волос
def can_grow_hair(user_id):
    cursor.execute("SELECT last_growth FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    today = datetime.date.today().strftime("%Y-%m-%d")
    return result is None or result[0] != today

# Функция увеличения длины волос
def grow_hair(user_id, username):
    if not can_grow_hair(user_id):
        return None, None  # Ограничение на 1 раз в день
    
    growth = round(random.uniform(1.0, 15.0), 1)
    cursor.execute("SELECT hair_length FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    new_length = round((result[0] if result else 0.0) + growth, 1)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    cursor.execute("INSERT INTO users (user_id, username, hair_length, last_growth) VALUES (?, ?, ?, ?)"
                   "ON CONFLICT(user_id) DO UPDATE SET hair_length = ?, last_growth = ?, username = ?",
                   (user_id, username, new_length, today, new_length, today, username))
    conn.commit()
    return new_length, growth

# Команда /stats для просмотра топ-10 в группе
@dp.message(Command("stats"))
async def stats_command(message: Message):
    top_users = get_top_users()
    if not top_users:
        await message.answer("В этом чате пока нет данных о длине волос.")
        return
    
    leaderboard = "🏆 <b>Топ 10 машонок в группе:</b>\n\n"
    for i, (username, length) in enumerate(top_users, start=1):
        leaderboard += f"{i}. {username if username else 'Аноним'} — {length} см\n"
    
    await message.answer(leaderboard, parse_mode="HTML")

# Команда /rost для отращивания волос
@dp.message(Command("rost"))
async def grow_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    new_length, growth = grow_hair(user_id, username)
    if new_length is None:
        await message.answer("❌ Ты уже отращивал волосы сегодня! Попробуй завтра.")
    else:
        await message.answer(f"🌿 Ты отрастил {growth} см волос! Теперь их длина {new_length} см.")

# Команды для Telegram-меню
async def set_bot_commands():
    commands = [
        BotCommand(command="rost", description="Отрастить волосы (1 раз в день)"),
        BotCommand(command="stats", description="Топ 10 машонок в группе")
    ]
    await bot.set_my_commands(commands)

async def main():
    logging.info("Запуск бота...")
    await set_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

