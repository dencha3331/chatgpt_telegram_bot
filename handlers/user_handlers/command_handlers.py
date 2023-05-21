from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from logs import logger
from lexicons import LEXICON_RU
from db import DateBase

DB_PATH = "db/db_bot.db"

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']

command_router: Router = Router()


@command_router.message(CommandStart())
async def welcome_command(message: Message):
    """ Command /start send start message """
    logger.info(f"start chat for {message.from_user.first_name}({message.from_user.id})")
    await message.answer(f"{message.from_user.first_name}!\n{LEXICON['/start']}")


@command_router.message(Command(commands=['help']))
async def help_command(message: Message):
    """ Command /help send help message """
    await message.reply(LEXICON["/help"])


@command_router.message(Command(commands=["new"]))
async def new_dialog(message: Message):
    """ Command /new makes the list messages[userid] empty """
    with DateBase(DB_PATH) as db:
        table_name = "messages_chatgpt"
        try:
            userid = message.from_user.id
            if userid in db.get_column(table_name, "user_id"):
                values = {"messages": "[]",
                          "max_tokens": 0}
                db.update_values("messages_chatgpt", values, {"user_id": userid})
                logger.info(f"Начат новый диалог с {message.from_user.first_name}")
                await message.answer(f"{LEXICON['/new']}")
            else:
                await message.answer("Пройдите регистрацию")

        except Exception as e:
            logger.error(f"new dialog command error: {e}")
            await message.answer(LEXICON["something_wrong"])


@command_router.message(Command(commands='showdata'))
async def process_showdata_command(message: Message):
    """ Command "/showdata send user profile or empty profile """
    userid = message.from_user.id
    with DateBase("db/db_bot.db") as db:
        table_name = "users"
        users_id = db.get_column(table=table_name, name_column="user_id")
        if userid in users_id:
            name_column = ("name", "surname", "age", "gender", "wish_news", "tokens")
            row = db.get_row(table=table_name, name_column=name_column, search_param={"user_id": userid})
            await message.answer(text=f'{LEXICON["show_db_name"]}: {row["name"]}\n'
                                      f'{LEXICON["show_db_surname"]}: {row["surname"]}\n'
                                      f'{LEXICON["show_db_age"]}: {row["age"]}\n'
                                      f'{LEXICON["show_db_gender"]}: {LEXICON[row["gender"]]}\n'
                                      f'{LEXICON["show_db_news"]}: {"Да" if row["wish_news"] else "нет"}\n'
                                      f'{LEXICON["show_db_tokens"]}: {row["tokens"]}\n')
        else:
            await message.answer(text=LEXICON["empty_db"])
