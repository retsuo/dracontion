import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

# Токен вашего бота DracontionBot
TOKEN = "8834102894:AAHB4C-rGL7lYR-uTIY4wkfadQa1qgsSW2Y"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    """Создает базу данных и таблицу пользователей, если их еще нет"""
    conn = sqlite3.connect("roulette_base.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 50000
        )
    """)
    conn.commit()
    conn.close()

def register_user(user_id: int, username: str):
    """Регистрирует нового пользователя и дает стартовый баланс"""
    conn = sqlite3.connect("roulette_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)",
            (user_id, username, 50000)
        )
        conn.commit()
        conn.close()
        return True  # Зарегистрирован впервые
    conn.close()
    return False  # Уже есть в базе

def get_balance(user_id: int):
    """Получает текущий баланс игрока"""
    conn = sqlite3.connect("roulette_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


# --- ХЕНДЛЕРЫ КОМАНД ---

# Команда /start (в личке у бота)
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    is_new = register_user(user_id, username)
    balance = get_balance(user_id)
    
    if is_new:
        await message.answer(
            f"Добро пожаловать в Dracontion Рулетку, <b>{message.from_user.first_name}</b>!\n\n"
            f"🎁 Вам начислен стартовый баланс: <b>{balance:,}</b> фишек.\n"
            f"Добавьте бота в ваш чат, чтобы играть с друзьями!",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"Рады видеть вас снова, <b>{message.from_user.first_name}</b>!\n"
            f"💰 Ваш текущий баланс: <b>{balance:,}</b> фишек.",
            parse_mode="HTML"
        )

# Команда проверки баланса /balance (в личке и в группах)
@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    register_user(user_id, username)
    balance = get_balance(user_id)
    
    await message.reply(
        f"💳 Баланс игрока <b>{message.from_user.first_name}</b>: <b>{balance:,}</b> фишек.",
        parse_mode="HTML"
    )


# Главная функция запуска
async def main():
    init_db()  # Создаем БД перед стартом
    print("Бот DracontionBot успешно запущен и ожидает команд!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
