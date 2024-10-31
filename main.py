import json
import config
import asyncio
import logging
import requests

from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token)
dp = Dispatcher(bot)

async def get_weather(city):
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
	   
	   return f'''🕰 <b>Текущие дата и время</b>: <code>{current_date}</code>

🏙 <b>Город</b>: <code>{city}</code>
🌡 <b>Температура</b>: <code>{current_temperature:.0f}°C</code>
⚡️ <b>Давление</b>: <code>{current_pressure}hPa</code>
💧 <b>Влажность</b>: <code>{current_humidity}%</code>
🌅 <b>Восход солнца</b>: <code>{sunrise}</code>
🌆 <b>Закат солнца</b>: <code>{sunset}</code>

📋 <b>Детальное описание</b>: <code>{weather_description}</code>'''

	else:
	   return '❗️ <b>Данного города не существует</b>!'
                                                    
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
        
    await message.answer("""👋 <b>Приветствую!
📝 Отправьте название города для того чтобы я отправил вам погоду об этом городе!</b>""", parse_mode='html')

@dp.message_handler()
async def get_weather_text(message: Message):
    await message.reply(await get_weather(message.text), parse_mode='html')

if __name__ == "__main__":
   executor.start_polling(dp, skip_updates=False)