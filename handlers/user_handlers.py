from logs import logger
import openai
import json
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from config_data import load_config
from lexicons import LEXICON_RU
from config_data import bot
from services import count_tokens_from_messages
from db import DateBase

db = DateBase("db/db_bot.db")
db.create_db("messages_chatgpt", {"user_id": "INTEGER",
                                  "messages": "TEXT",
                                  "tokens": "INTEGER",
                                  "max_tokens": "INTEGER"})

lexicon: dict[str, str] = LEXICON_RU['user_handlers']
user_handler_router: Router = Router()
openai.api_key = load_config().open_ai.token  # API openAI


@user_handler_router.message(CommandStart())
async def welcome_command(message: Message):
    """
    Command start
    """
    try:
        userid = message.from_user.id
        values = {"user_id": userid,
                  "messages": "[]",
                  "tokens": 100000,
                  "max_tokens": 0}
        if userid not in db.get_column("messages_chatgpt", "user_id"):
            db.insert("messages_chatgpt", values)
        else:
            db.update_values("messages_chatgpt", values, {"user_id": userid})

        await message.answer(f"{message.from_user.first_name}!\n{lexicon['/start']}")

        logger.info(f"start chat for {message.from_user.first_name}({message.from_user.id})")
    except Exception as e:
        logger.error(f"start command error: {e}")


@user_handler_router.message(Command(commands=['help']))
async def help_command(message: Message):
    """
    Command /help send help message 
    """
    await message.reply(lexicon["/help"])


@user_handler_router.message(Command(commands=["new"]))
async def new_dialog(message: Message):
    """
    Command /new makes the list messages[userid] empty
    """
    try:
        userid = message.from_user.id
        if userid in db.get_column("messages_chatgpt", "user_id"):
            values = {"user_id": userid,
                      "messages": "[]",
                      "max_tokens": 0}
            db.update_values("messages_chatgpt", values, {"user_id": userid})
        else:
            await message.answer("Пройдите регистрацию")

        await message.answer(f"{lexicon['/new']}")
        logger.info(f"Начат новый диалог с {message.from_user.first_name}")
    except Exception as e:
        logger.error(f"new dialog command error: {e}")


@user_handler_router.message(F.text)
async def chatgpt_answer(message: Message):
    """
    Handles all messages not in listed above and interaction with gpt3.5-turbo.
    """
    processing_message = await message.reply(lexicon['processing_message'])
    try:
        model = "gpt-3.5-turbo-0301"
        user_message = message.text
        userid = message.from_user.id
        if userid not in db.get_column("messages_chatgpt", "user_id"):
            db.insert("messages_chatgpt", {"user_id": userid,
                                           "messages": '[]',
                                           "tokens": 100000,
                                           "max_tokens": 0})
        chat_messages = json.loads(db.get_cell_value("messages_chatgpt", "messages", ("user_id", userid)))
        chat_messages.append({'role': 'user', 'content': user_message})

        if count_tokens_from_messages(chat_messages, model) > 3000:
            if not db.get_cell_value("messages", "max_tokens", ("user_id", userid,)):
                db.update_values("messages_chatgpt", {"max_tokens": 1}, {"user_id": userid})
                await message.answer(lexicon['tokens_limit'])
            while count_tokens_from_messages(chat_messages, model) > 2000:
                chat_messages.pop(0)

        completion = openai.ChatCompletion.create(
            model=model,
            messages=chat_messages,
            max_tokens=1024,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            user=message.from_user.first_name
        )
        chatgpt_response = completion.choices[0]['message']
        chat_messages.append({'role': 'assistant', 'content': chatgpt_response['content']})
        str_chat_messages = json.dumps(chat_messages)
        tokens = db.get_cell_value(
            "messages_chatgpt", "tokens", ("user_id", userid)
        ) - completion['usage']['total_tokens']
        db.update_values("messages_chatgpt", {"messages": str_chat_messages,
                                              "tokens": tokens}, {"user_id": userid})
        # Уведомление, что токены заканчиваются и отправить сообщение пользователю о количестве
        db.notification_tokens(userid)

        logger.debug(f'{message.from_user.first_name}({message.from_user.id}): {user_message}')
        logger.debug(f'ChatGPT response: {chatgpt_response["content"]}')
        # logger.info(f'{userid}:\nTotal tokens: {completion["usage"]["total_tokens"]}')
        if db.get_cell_value("messages_chatgpt", "tokens", ("user_id", userid)) < 10000:
            await message.answer("У вас меньше 10000 токенов")

        await message.reply(chatgpt_response['content'])
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

    except Exception as e:
        logger.error(f"error in answer: {e}")
        logger.error(f"type: {type(e)}")
        # await message.reply(lexicon['end_cash'])
        # await new_dialog(message)
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)
        await message.answer(lexicon['something_wrong'])


@user_handler_router.message()
async def unknown_message(message: Message):
    await message.answer(lexicon['unknown_message'])
