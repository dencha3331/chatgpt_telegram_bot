import logging
import openai
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from config_data import load_config
from lexicons import LEXICON_RU

lexicon: dict[str, str] = LEXICON_RU['user_handlers']

user_handler_router: Router = Router()
logging.basicConfig(level=logging.INFO, filename="user_handlers.log", filemode="a")  # set logger
openai.api_key = load_config().open_ai.token  # API openAI
messages: dict[int: list[str]] = {}  # Все сообщения в чате с chatGPT(не более 4096 токенов после сброс)


@user_handler_router.message(CommandStart())
async def welcome_command(message: Message):
    """Command start"""
    try:
        userid = message.from_user.id
        messages[userid] = []
        await message.answer(f"{message.from_user.first_name}!\n{lexicon['/start']}")
        logging.info(f"start chat for {message.from_user.first_name}({message.from_user.id})")
    except Exception as e:
        logging.error(f"start command error: {e}")


@user_handler_router.message(Command(commands=['help']))
async def help_command(message: Message):
    await message.reply(lexicon["/help"])


@user_handler_router.message(Command(commands=["new"]))
async def new_dialog(message: Message):
    try:
        userid = message.from_user.id
        messages[userid] = []
        await message.answer(f"{lexicon['/new']}")
        logging.info(f"Начат новый диалог с {message.from_user.first_name}")
    except Exception as e:
        logging.error(f"new dialog command error: {e}")


@user_handler_router.message()
async def chatgpt_answer(message: Message):
    """
    Handles all messages not in listed above and interaction with gpt3.5-turbo.
    """
    try:
        user_message = message.text
        userid = message.from_user.id
        if userid not in messages:
            messages[userid] = []
        messages[userid].append({"role": "user", "content": user_message})
        logging.info(f'{message.from_user.first_name}({message.from_user.id}): {user_message[:100]}')

        # processing_message = await message.reply("Пожалуйста, подождите, я обрабатываю ваш запрос...")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages[userid],
            max_tokens=1024,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            user=message.from_user.first_name
        )
        chatgpt_response = completion.choices[0]['message']
        messages[userid].append({"role": "assistant", "content": chatgpt_response['content']})
        logging.info(f'ChatGPT response: {chatgpt_response["content"]}')
        await message.reply(chatgpt_response['content'])
        # await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

    except Exception as e:
        logging.error(f"error in answer: {e}")
        if e == 'context_length_exceeded':
            await message.reply(lexicon['end_cash'])
            await new_dialog(message)
