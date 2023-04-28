from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram import Router, F
from geopy.geocoders import Nominatim
import requests


weather_router: Router = Router()


class WeatherState(StatesGroup):
    get_weather = State()


@weather_router.message(Command(commands='weather'), StateFilter(default_state))
async def get_weather_command(message: Message, state: FSMContext):
    await message.answer("Напишите название города либо отправьте геолокацию. Для отмены нажмите /cancel")
    await state.set_state(WeatherState.get_weather)


@weather_router.message(StateFilter(WeatherState.get_weather), F.location | F.text)
async def get_weather_correct_data(message: Message, state: FSMContext):
    geolocator = Nominatim(user_agent="my_personal_bot/v1.23")
    if message.location:
        longitude = message.location.longitude
        latitude = message.location.latitude
    else:
        location = geolocator.geocode(f"{message.text}, Россия")
        if not location:
            await message.answer("Немогу найти такого города проверьте правильность написание или отправьте геолакацию")
            return
        longitude = location.longitude
        latitude = location.latitude

    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&"
                            f"hourly=temperature_2m,precipitation_probability,precipitation,cloudcover,"
                            f"windspeed_10m,windgusts_10m&daily=sunrise,sunset&current_weather=true&"
                            f"forecast_days=3&timezone=auto").json()

    res = response["hourly"]
    sunset_sunrise = response["daily"]
    messages = []
    date = sun = 0
    for (time, temp, probability,
         precipitation, windspeed, windgusts, cloud,) in zip(res['time'], res["temperature_2m"],
                                                             res["precipitation_probability"], res["precipitation"],
                                                             res["windspeed_10m"], res["windgusts_10m"],
                                                             res['cloudcover']):
        if int(time[8:10]) > date:
            messages.append(f"\n_______{time[8:10]}.{time[5:7]}.{time[:4]}. "
                            f"день {sunset_sunrise['sunrise'][sun][-5:]}-{sunset_sunrise['sunset'][sun][-5:]}_______")
            sun += 1
            date = int(time[8:10])
        if int(time[-5:-3]) % 3 == 0:
            messages.append(f"\n{time[-5:]}: {temp}°C, осадки: {probability}%, {precipitation}mm, "
                            f"Ветер: {round(windspeed / 3.6, 2)}m/c, "
                            f"порывы {round(windgusts / 3.6, 2)}m/c облака: {cloud}%")
    message_text = "\n".join(messages)

    await message.answer(message_text)
    await state.clear()


@weather_router.message(StateFilter(WeatherState.get_weather))
async def get_weather_wrong_data(message: Message):
    await message.answer(
        "Не корректный ввод! Введите название города или пришлите геолокацию. Для отмены нажмите /cancel")
