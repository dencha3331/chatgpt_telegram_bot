#!/usr/bin/python3

from aiogram import Bot, Dispatcher
import logging
import asyncio

from aiogram.fsm.storage.redis import RedisStorage, Redis

from handlers import user_handler_router, registration_router
from config_data import load_config, Config
from keyboards import set_main_menu

logger = logging.getLogger(__name__)
# Инициализируем Redis
redis: Redis = Redis(host='localhost')

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
storage: RedisStorage = RedisStorage(redis=redis)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s',
        filename="bot.log",
        filemode="w"
    )
    logging.info("Starting botttttt")
    logger.info("Starting bot")
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode="HTML")
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(registration_router)
    dp.include_router(user_handler_router)
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
