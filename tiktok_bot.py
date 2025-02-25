import asyncio
import logging
import re
import requests
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# Токен Telegram-бота
TOKEN = "7345740465:AAFKrj8vzazL4TK-AIBeXCzsoAW4DiIFJn4"

# Функция для скачивания видео с TikTok (без водяного знака)
def download_tiktok_video(url):
    try:
        api_url = "https://lovetik.com/api/ajax/search"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        data = {"query": url}
        
        response = requests.post(api_url, data=data, headers=headers).json()
        print("Ответ API:", response)  # Логируем API-ответ
        
        if "links" in response and isinstance(response["links"], list) and len(response["links"]) > 0:
            for link in response["links"]:
                if "a" in link and "no_wm" in link["a"]:
                    return link["a"]
            return response["links"][0].get("a")
        
        return None
    except Exception as e:
        logging.error(f"Ошибка при скачивании видео TikTok: {e}")
        return None

# Функция для скачивания видео с YouTube
def download_youtube_video(url):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'youtube_video.mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return "youtube_video.mp4"
        
    except Exception as e:
        logging.error(f"Ошибка при скачивании видео YouTube: {e}")
        return None

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне ссылку на TikTok или YouTube-видео, и я скачаю его!")

@dp.message()
async def video_handler(message: Message):
    url = message.text.strip()
    
    if re.match(r'https?://(?:www\.)?(vm\.|vt\.)?tiktok\.com/.*', url):
        await message.answer("Скачиваю видео с TikTok... ⏳")
        video_url = download_tiktok_video(url)
        
        if video_url:
            await message.answer_video(video_url, caption="Вот ваше видео с TikTok! 🎬")
        else:
            await message.answer("Не удалось скачать видео с TikTok. Попробуйте позже.")
    
    elif re.match(r'https?://(?:www\.)?youtube\.com/.*|https?://youtu\.be/.*', url):
        await message.answer("Скачиваю видео с YouTube... ⏳")
        video_path = download_youtube_video(url)
        
        if video_path:
            await message.answer_video(types.FSInputFile(video_path), caption="Вот ваше видео с YouTube! 🎬")
        else:
            await message.answer("Не удалось скачать видео с YouTube. Попробуйте позже.")
    
    else:
        await message.answer("Пожалуйста, отправьте корректную ссылку на видео TikTok или YouTube.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
