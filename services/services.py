from __future__ import annotations
from aiogram.types import Message, CallbackQuery
import tiktoken
from typing import NamedTuple

from db import DateBase
from lexicons import LEXICON_RU
from logs import logger
from errors import UserNotRegistration, MessageFromUserIsNone

DB_PATH = "db/db_bot.db"
lexicon = LEXICON_RU['service']
TABLE_NAME: str = "users"
TABLE_NAME_FOR_MESSAGES: str = "messages_chatgpt"
LEXICON: dict[str, str] = LEXICON_RU['user_handlers']


class Checking:
    @staticmethod
    def count_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")

    @staticmethod
    async def check_total_tokens(message: Message | CallbackQuery) -> None:
        """Check count tokens in send message and check tokens in db on table users"""
        try:
            userid: int = message.from_user.id
            with DateBase(DB_PATH) as db:
                tokens = db.get_cell_value("messages_chatgpt", "tokens", ("user_id", userid))
                if tokens and tokens < 10000:
                    await message.answer(f"У вас осталось {tokens} токенов")
        except Exception as e:
            logger.error(f"error in services.py check_tokens: {e}")
            logger.error(f"{type(e)}")

    @staticmethod
    async def check_max_tokens(message: Message | CallbackQuery) -> None:
        with DateBase(DB_PATH) as db:
            try:
                userid: int = message.from_user.id
                max_tokens = db.get_cell_value("messages_chatgpt", "max_tokens", ("user_id", userid,))
                if max_tokens and max_tokens == 1:
                    db.update_values("messages_chatgpt", {"max_tokens": 2}, {"user_id": userid})
                    await message.answer(lexicon['tokens_limit'])
            except Exception as e:
                logger.error(f"error in services.py check_max_tokens: {e}")
                logger.error(f"{type(e)}")

    @staticmethod
    async def check_tokens(message: Message | CallbackQuery):
        await Checking.check_total_tokens(message)
        await Checking.check_max_tokens(message)

    @staticmethod
    async def check_user_not_in_db(message: Message) -> None:
        with DateBase(DB_PATH) as db:
            userid: int = message.from_user.id
            if userid not in db.get_column("users", "user_id"):
                await message.answer("Пройдите регистрацию")
                raise UserNotRegistration

    @staticmethod
    async def check_message_from_user_not_none(message: Message) -> None:
        if not message.from_user:
            await message.answer("Only private chat")
            raise MessageFromUserIsNone


class WorkingDb:

    @staticmethod
    def save_user_registration_data_in_db(userid: int, reg_data: dict) -> None:
        with DateBase(DB_PATH) as db:
            if userid not in db.get_column(table=TABLE_NAME, name_column="user_id"):
                reg_data.update(tokens=100000)
                db.insert(table=TABLE_NAME, column_values=reg_data)
                db.insert(table=TABLE_NAME_FOR_MESSAGES, column_values={"user_id": userid,
                                                                        "messages": "[]",
                                                                        "tokens": 100000,
                                                                        "max_tokens": 0})
            else:
                db.update_values(table=TABLE_NAME, values=reg_data, params={"user_id": userid})

    @staticmethod
    def reset_message_chat_gpt(userid: int) -> str:
        with DateBase(DB_PATH) as db:
            table_name: str = "messages_chatgpt"
            if userid not in db.get_column(table_name, "user_id"):
                return "Пройдите регистрацию"
            values = {"messages": "[]",
                      "max_tokens": 0}
            db.update_values("messages_chatgpt", values, {"user_id": userid})
            logger.info(f"Начат новый диалог с {userid}")
            return f"{LEXICON['/new']}"

    @staticmethod
    def get_user_data_from_db(userid: int) -> str:
        with DateBase("db/db_bot.db") as db:
            table_name: str = "users"
            users_id: tuple[int] = db.get_column(table=table_name, name_column="user_id")
            if userid not in users_id:
                return LEXICON["empty_db"]
            name_column: tuple = ("name", "surname", "age", "gender", "wish_news", "tokens")
            row: dict[str, str] = db.get_row(table=table_name, name_column=name_column,
                                             search_param={"user_id": userid})
            return f'{LEXICON["show_db_name"]}: {row["name"]}\n' \
                   f'{LEXICON["show_db_surname"]}: {row["surname"]}\n' \
                   f'{LEXICON["show_db_age"]}: {row["age"]}\n' \
                   f'{LEXICON["show_db_gender"]}: {LEXICON[row["gender"]]}\n' \
                   f'{LEXICON["show_db_news"]}: {"Да" if row["wish_news"] else "нет"}\n' \
                   f'{LEXICON["show_db_tokens"]}: {row["tokens"]}'


class UseridText(NamedTuple):
    userid: int
    text: str


def get_userid_and_text(message: Message) -> UseridText:
    return UseridText(message.from_user.id, message.text)
