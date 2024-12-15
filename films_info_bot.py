#Телеграм-бот. дает информацию о фильмах с помощью omdbapi


import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from deep_translator import GoogleTranslator
from config import TOKEN, OMDB_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

def translate_to_russian(text):
    return GoogleTranslator(source='en', target='ru').translate(text)

def translate_to_english(text):
    return GoogleTranslator(source='ru', target='en').translate(text)

def search_movies(query):
    query_in_english = translate_to_english(query)
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={query_in_english}&plot=full"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            title = translate_to_russian(data.get('Title', 'Неизвестно'))
            genre = translate_to_russian(data.get('Genre', 'Неизвестно'))
            director = translate_to_russian(data.get('Director', 'Неизвестно'))
            plot = translate_to_russian(data.get('Plot', 'Описание недоступно'))
            year = data.get('Year', 'Неизвестно')
            rating = data.get('imdbRating', 'Нет рейтинга')
            imdb_id = data.get('imdbID', 'Неизвестно')

            return (
                f"Название: {title}\n"
                f"Год: {year}\n"
                f"Жанры: {genre}\n"
                f"Режиссер: {director}\n"
                f"Рейтинг: {rating}\n"
                f"Описание: {plot}\n"
                f"IMDb ID: {imdb_id}"
            )
        else:
            return "Фильмы не найдены. Попробуй другой запрос."
    else:
        return "Что-то пошло не так..."

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Напиши название фильма, я расскажу тебе про него."
    )

@dp.message(Command("help"))
async def help(message: Message):
    await message.answer('Смотри, что я могу: \n/start - Запустить бота')

@dp.message()
async def send_movie_info(message: Message):
    query = message.text.strip()
    if not query:
        await message.answer("Напиши название фильма, я расскажу тебе про него.")
        return
    result = search_movies(query)
    await message.answer(result)

async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())

