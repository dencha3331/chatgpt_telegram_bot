#!/usr/bin/env python3

from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram import Dispatcher
import logging
import asyncio


from config_data.config import bot
from handlers import user_handler_router, registration_router, voice_router
from keyboards import set_main_menu


async def main():
    # set logger
    logging.basicConfig(
        level=logging.INFO,
        filename="./logs/bot.log",
        filemode="a",
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s',

    )
    # Инициализируем Redis
    redis: Redis = Redis(host='localhost')
    # Инициализируем хранилище (создаем экземпляр класса RedisStorage)
    storage: RedisStorage = RedisStorage(redis=redis)

    logging.info("Starting bot")
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(voice_router)
    dp.include_router(registration_router)
    dp.include_router(user_handler_router)
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
