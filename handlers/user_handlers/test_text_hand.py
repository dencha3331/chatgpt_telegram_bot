from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from logs import logger
from config_data import bot
from lexicons import LEXICON_RU
from errors import UserNotRegistration, MessageFromUserIsNone
from services import chatgpt, Checking

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
text_router: Router = Router()


@text_router.message(F.text)
async def text_messages(message: Message) -> None:
    """
    Handles all text message and send chatgpt_answer() on chatgpt.py
    """
    processing_message = await message.reply(LEXICON['processing_message'])
    try:
        await Checking.check_message_from_user_not_none(message)
        await Checking.check_user_not_in_db(message)
        answer_chatgpt: str = await chatgpt(message.from_user.id, message.text)
        await Checking.check_tokens(message)
        await message.answer(answer_chatgpt)
        logger.debug(f'{message.from_user.first_name}({message.from_user.id}): {message.text}')
    except UserNotRegistration:
        pass
    except MessageFromUserIsNone:
        pass
    except Exception as e:
        logger.error(f"error in text_handlers.py text_messages: {e}")
        logger.error(type(e))
        await message.answer(LEXICON["something_wrong"])
    finally:
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)
