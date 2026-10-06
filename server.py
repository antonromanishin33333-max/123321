import asyncio
import json
import sqlite3
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-username.github.io/telegram-webapp/")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            datetime TEXT,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_booking(user_id, title, datetime_val, note):
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (user_id, title, datetime, note)
        VALUES (?, ?, ?, ?)
    ''', (user_id, title, datetime_val, note))
    conn.commit()
    conn.close()

def get_bookings(user_id):
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, datetime, note FROM bookings WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Открыть журнал броней", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    
    user_bookings = get_bookings(message.from_user.id)
    text = "👋 Привет! Это твой журнал бронирований.\n\n"
    
    if user_bookings:
        text += "<b>Текущие брони:</b>\n"
        for title, dt, note in user_bookings:
            text += f"• <b>{title}</b> ({dt})\n  <i>Заметка: {note or 'нет'}</i>\n"
    else:
        text += "У тебя пока нет сохраненных броней."

    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.message(lambda m: m.web_app_data is not None)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "add":
            add_booking(
                user_id=message.from_user.id,
                title=data.get("title"),
                datetime_val=data.get("datetime"),
                note=data.get("note")
            )
            await message.answer(f"✅ Бронь «<b>{data.get('title')}</b>» успешно сохранена!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка при сохранении: {e}")

# Простой эндпоинт для проверки работы сервера и UptimeRobot
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    init_db()
    
    # Запуск веб-сервера для Render
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Сервер запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())