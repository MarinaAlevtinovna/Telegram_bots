#Телеграмм-бот, отправляет погоду в городе Москва. 


from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import aiohttp
from config import TOKEN_WEATHER_BOT, WEATHER_API_KEY
import sqlite3


bot = Bot(token=TOKEN_WEATHER_BOT)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)""")
    conn.commit()
    conn.close()

def save_user_id(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_user_ids():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids

async def get_weather(api_key: str, city: str = 'Moscow') -> str:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                weather_description = data["weather"][0]["description"]
                return f"Погода в {city}: {weather_description}, температура {temp}°C"
            else:
                return "Не удалось получить прогноз погоды. Попробуйте позднее."

async def send_daily_weather():
    weather_info = await get_weather(WEATHER_API_KEY, "Москва")
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=weather_info)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    save_user_id(user_id)
    await message.answer('Привет! Это погодный бот! Буду присылать погоду в Москве каждый день.')

@dp.message(Command("help"))
async def help(message: Message):
    await message.answer('Смотри, что я могу: \n /start \n /help, \n /weather')

@dp.message(Command("weather"))
async def weather(message: Message):
    weather_info = await get_weather(WEATHER_API_KEY, "Москва")
    await message.answer(weather_info)

async def main():
    init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_weather, "cron", hour=9, minute=0)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())