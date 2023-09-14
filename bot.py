#!/usr/bin/env python3

from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher
import asyncio

from logs import logger
from config_data.config import bot
from keyboards import set_main_menu
from handlers import (command_router,
                      registration_router,
                      weather_router,
                      text_router,
                      voice_router,
                      payment_router,
                      other_router)


async def main():
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)

    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(command_router)
    dp.include_router(registration_router)
    dp.include_router(weather_router)
    dp.include_router(voice_router)
    # dp.include_router(text_router)
    dp.include_router(payment_router)
    dp.include_router(other_router)

    await set_main_menu(bot)
    logger.info("Starting bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
