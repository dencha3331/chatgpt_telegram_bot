#!/usr/bin/python3

from aiogram import Bot, Dispatcher
import logging
import asyncio

from handlers import user_handler_router
from config_data import load_config, Config
from keyboards import set_main_menu

logger = logging.getLogger(__name__)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )
    logger.info("Starting bot")
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode="HTML")
    dp: Dispatcher = Dispatcher()
    dp.include_router(user_handler_router)
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
