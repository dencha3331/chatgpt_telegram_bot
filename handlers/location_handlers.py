import logging
from aiogram import Router, F
from aiogram.types import Message
import requests
from geopy.geocoders import Nominatim
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Command, StateFilter, Text


location_router: Router = Router()

class WeatherState(StatesGroup):
    get_weather = State()


@location_router.message(Command(commands='weather'), StateFilter(default_state))
async def get_weather_command(message: Message, state: FSMContext):
    await message.answer("Напишите название города либо отправьте геолокацию. Для отмены нажмите /cancel")
    await state.set_state(WeatherState.get_weather)



@location_router.message(StateFilter(WeatherState.get_weather), F.location | F.text)
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
                        f"hourly=temperature_2m,precipitation_probability,precipitation,windspeed_10m&"
                        f"current_weather=true&forecast_days=3&timezone=auto").json()

    res = response["hourly"]
    tot = []
    for time, temp, osad, wind in zip(res['time'], res["temperature_2m"], 
                                      res["precipitation"], res["windspeed_10m"]):
        tot.append(f"Дата: {time[5:]}, Темпиратура: {temp}, Осадки: {osad}, Ветер: {wind}")
    print("ok")
    #print(tot)
    str_res = "\n".join(tot[::3])
    print(str_res)
    await message.answer(str_res)
    await state.clear()

    #print(message.location.longitude)
    #print(type(message.location.longitude))
    
@location_router.message(StateFilter(WeatherState.get_weather))
async def get_weather_wrong_data(message: Message):
    await message.answer("Не корректный ввод! Введите название города или пришлите геолакацию. Для отмены нажмите /cancel")




