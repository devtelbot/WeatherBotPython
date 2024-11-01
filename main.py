import time
import json
import config
import asyncio
import logging
import requests

from datetime import datetime
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token)
dp = Dispatcher(bot)

user_language = {}

async def get_weather(city, language="uk"):
    now = datetime.now()
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + config.api_key_weather + "&q=" + city
    response = requests.get(complete_url)
    x = json.loads(response.content)
    
    if x.get("cod") != "404":
        y = x.get("main")
        y1 = x.get("sys")
        current_date = now.strftime("%d.%m.%Y %H:%M:%S")
        current_temperature = y.get("temp") - 273.15
        current_pressure = y.get("pressure")
        current_humidity = y.get("humidity")
        
        sunrise = datetime.fromtimestamp(y1.get("sunrise")).strftime("%H:%M:%S")
        sunset = datetime.fromtimestamp(y1.get("sunset")).strftime("%H:%M:%S")
                
        z = x.get("weather")
        weather_description = z[0]["description"]
        
        if language == "ru":
            return f'''🕰 <b>Текущая дата и время:</b> <code>{current_date}</code>
            
🏙 <b>Город</b>: <code>{city}</code>
🌡 <b>Температура</b>: <code>{current_temperature:.0f}°C</code>
⚡️ <b>Давление</b>: <code>{current_pressure}hPa</code>
💧 <b>Влажность</b>: <code>{current_humidity}%</code>
🌅 <b>Восход солнца</b>: <code>{sunrise}</code>
🌆 <b>Закат солнца</b>: <code>{sunset}</code>

📋 <b>Описание погоды</b>: <code>{weather_description}</code>'''
        
        elif language == "en":
            return f'''🕰 <b>Current date and time:</b> <code>{current_date}</code>
            
🏙 <b>City</b>: <code>{city}</code>
🌡 <b>Temperature</b>: <code>{current_temperature:.0f}°C</code>
⚡️ <b>Pressure</b>: <code>{current_pressure}hPa</code>
💧 <b>Humidity</b>: <code>{current_humidity}%</code>
🌅 <b>Sunrise</b>: <code>{sunrise}</code>
🌆 <b>Sunset</b>: <code>{sunset}</code>

📋 <b>Weather description</b>: <code>{weather_description}</code>'''
        
        else:
            return f'''🕰 <b>Поточна дата та час:</b> <code>{current_date}</code>
            
🏙 <b>Місто</b>: <code>{city}</code>
🌡 <b>Температура</b>: <code>{current_temperature:.0f}°C</code>
⚡️ <b>Тиск</b>: <code>{current_pressure}hPa</code>
💧 <b>Вологість</b>: <code>{current_humidity}%</code>
🌅 <b>Схід сонця</b>: <code>{sunrise}</code>
🌆 <b>Захід сонця</b>: <code>{sunset}</code>

📋 <b>Детальний опис</b>: <code>{weather_description}</code>'''
    else:
        return {
            "uk": '❗️ <b>Перевірте правильність вводу міста</b>!',
            "ru": '❗️ <b>Проверьте правильность ввода города</b>!',
            "en": '❗️ <b>Check the city name and try again</b>!'
        }[language]


@dp.message_handler(commands=['start'])
async def language_command(message: Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    await message.answer("""🇺🇦 <b>Оберіть мову...
🇷🇺 Выберите язык...
🇬🇧 Select a language...</b>""", reply_markup=keyboard, parse_mode='html')

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang_'))
async def process_callback_language(call):
    user_id = call.from_user.id
    language = call.data.split('_')[1]
    user_language[user_id] = language
    
    language_selected = {
        "uk": "<b>Мову змінено на українську</b> 🇺🇦",
        "ru": "<b>Язык изменен на русский</b> 🇷🇺",
        "en": "<b>Language changed to English</b> 🇬🇧"
    }
    
    await bot.send_message(user_id, language_selected[language], parse_mode='html')
    
    time.sleep(3)
    
    language = user_language.get(call.from_user.id, "uk")
    url = '<a href="https://github.com/devtelbot/WeatherBotPython">CODE</a>'
    
    greetings = {
        "uk": f"""👋 <b>Вітаю!
📝 Відправте назву міста для того щоб я відправив вам погоду в цьому місті!

🔗 Відкритий вихідний код цього бота вже на GitHub</b>: {url}""",
        "ru": f"""👋 <b>Привет!
📝 Отправьте название города, чтобы я отправил вам погоду в этом городе!

🔗 Исходный код этого бота доступен на GitHub</b>: {url}""",
        "en": f"""👋 <b>Hello!
📝 Send the name of a city, and I'll send you the weather in that city!

🔗 This bot's source code is available on GitHub</b>: {url}"""
    }
    
    await call.message.answer(greetings[language], parse_mode='html')

@dp.message_handler()
async def get_weather_text(message: Message):
    language = user_language.get(message.from_user.id, "uk")
    await message.reply(await get_weather(message.text, language), parse_mode='html')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
