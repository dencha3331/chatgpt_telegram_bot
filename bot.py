#!/usr/bin/env python3

from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram import Dispatcher
import asyncio

from db import DateBase
from logs import logger
from config_data.config import bot
from keyboards import set_main_menu
from handlers import (command_router,
                      registration_router,
                      weather_router,
                      text_router,
                      voice_router,
                      other_router)

DB_PATH = "db/db_bot.db"

table_name_chatgpt = "messages_chatgpt"
table_column_chatgpt = {"user_id": "INTEGER",
                        "messages": "TEXT",
                        "tokens": "INTEGER",
                        "max_tokens": "INTEGER"}

table_name_users = "users"
table_column_users = {"user_id": "INTEGER",
                      "tokens": "INTEGER",
                      "name": "TEXT",
                      "surname": "TEXT",
                      "age": "INTEGER",
                      "gender": "TEXT",
                      "wish_news": "INTEGER"}

with DateBase(DB_PATH) as db:
    db.create_table(table_name_chatgpt, table_column_chatgpt)
    db.create_table(table_name_users, table_column_users)


async def main():
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)

    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(command_router)
    dp.include_router(registration_router)
    dp.include_router(weather_router)
    dp.include_router(voice_router)
    dp.include_router(text_router)
    dp.include_router(other_router)

    await set_main_menu(bot)
    logger.info("Starting bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
