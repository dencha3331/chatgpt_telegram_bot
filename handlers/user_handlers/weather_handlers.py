from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram import Router, F
from geopy.geocoders import Nominatim

from services import get_weather
from lexicons import LEXICON_RU
from states import WeatherState

LEXICON: dict[str, str] = LEXICON_RU['weather_handlers']

weather_router: Router = Router()


@weather_router.message(Command(commands='weather'), StateFilter(default_state))
async def get_weather_command(message: Message, state: FSMContext) -> None:
    """The weather command handler puts it in the get weather state"""
    await message.answer(LEXICON["get_weather_command"])
    await state.set_state(WeatherState.get_weather)


@weather_router.message(StateFilter(WeatherState.get_weather), F.location | F.text)
async def get_weather_correct_data(message: Message, state: FSMContext) -> None:
    """Getting a weather forecast from the openweather website"""
    geolocator = Nominatim(user_agent="my_personal_bot/v1.23")
    if message.location:
        longitude = message.location.longitude
        latitude = message.location.latitude
    else:
        location = geolocator.geocode(f"{message.text}, Россия")
        if not location:
            await message.answer(LEXICON["get_weather_correct_data_incorrect"])
            return
        longitude = location.longitude
        latitude = location.latitude
    message_text = get_weather(latitude=latitude, longitude=longitude)

    await message.answer(message_text)
    await state.clear()


@weather_router.message(StateFilter(WeatherState.get_weather))
async def get_weather_wrong_data(message: Message) -> None:
    """Incorrect city data entry"""
    await message.answer(LEXICON["get_weather_wrong_data"])
