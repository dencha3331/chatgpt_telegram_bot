import logging
from os import urandom
from urllib.request import FancyURLopener
from numpy import union1d
import openai
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from config_data import load_config
from lexicons import LEXICON_RU
from config_data import bot
from services import count_tokens_from_messages

lexicon: dict[str, str] = LEXICON_RU['user_handlers']
user_handler_router: Router = Router()
openai.api_key = load_config().open_ai.token  # API openAI
messages: dict[int, dict[str, list[dict] | bool]] = {}
               # Все сообщения в чате с chatGPT(не более 4096 токенов после сброс)


@user_handler_router.message(CommandStart())
async def welcome_command(message: Message):
    """
    Command start
    """
    try:
        userid = message.from_user.id
        messages[userid] = {}
        messages[userid]["content"] = []
        messages[userid]["tokens"] = False
        await message.answer(f"{message.from_user.first_name}!\n{lexicon['/start']}")

        logging.info(f"start chat for {message.from_user.first_name}({message.from_user.id})")
    except Exception as e:
        logging.error(f"start command error: {e}")


@user_handler_router.message(Command(commands=['help']))
async def help_command(message: Message):
    """
    Command /help
    """
    await message.reply(lexicon["/help"])


@user_handler_router.message(Command(commands=["new"]))
async def new_dialog(message: Message):
    """
    Command /new makes the list messages[userid] empty
    """
    try:
        userid = message.from_user.id
        messages[userid] = {}
        messages[userid]["content"] = []
        messages[userid]["tokens"] = False

        await message.answer(f"{lexicon['/new']}")
        logging.info(f"Начат новый диалог с {message.from_user.first_name}")
    except Exception as e:
        logging.error(f"new dialog command error: {e}")


@user_handler_router.message(F.text)
async def chatgpt_answer(message: Message):
    """
    Handles all messages not in listed above and interaction with gpt3.5-turbo.
    """
    try:
        model = "gpt-3.5-turbo-0301"
        user_message = message.text
        userid = message.from_user.id
        if userid not in messages:
            messages[userid] = {}
            messages[userid]["content"] = []
            messages[userid]["tokens"] = False
        messages[userid]["content"].append({"role": "user", "content": user_message})
        processing_message = await message.reply(lexicon['processing_message'])
        if count_tokens_from_messages(messages[userid]["content"], model) > 3000:
            if not messages[userid]["tokens"]:
                messages[userid]["tokens"] = True
                await message.answer(lexicon['tokens_limit'])
            while count_tokens_from_messages(messages[userid]["content"], model) > 2000:
                messages[userid]["content"].pop(0)

        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages[userid]["content"],
            max_tokens=1024,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            user=message.from_user.first_name
        )
        chatgpt_response = completion.choices[0]['message']
        messages[userid]["content"].append({"role": "assistant", "content": chatgpt_response['content']})

        logging.info(f'{message.from_user.first_name}({message.from_user.id}): {user_message}')
        logging.info(f'ChatGPT response: {chatgpt_response["content"]}')
        logging.info(f'Total tokens: {completion["usage"]["total_tokens"]}')

        await message.reply(chatgpt_response['content'])
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

    except Exception as e:
        logging.error(f"error in answer: {e}")
        logging.error(f"type: {type(e)}")
        await message.reply(lexicon['end_cash'])
        await new_dialog(message)


@user_handler_router.message()
async def unknown_message(message: Message):
    await message.answer(lexicon['unknown_message'])
