from aiogram import Router, F
from aiogram.types import Message

from logs import logger
from config_data import bot
from lexicons import LEXICON_RU
from services import (chatgpt_answer,
                      check_tokens,
                      check_max_tokens,
                      check_user)

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
text_router: Router = Router()


@text_router.message(F.text)
async def text_messages(message: Message) -> None:
    """
    Handles all text message and send chatgpt_answer() on chatgpt.py
    """
    processing_message = await message.reply(LEXICON['processing_message'])
    try:
        userid = message.from_user.id
        check_user_in_db = check_user(userid)
        if check_user_in_db:
            await message.answer(check_user_in_db)
            return
        message_text = message.text
        logger.debug(f'{message.from_user.first_name}({message.from_user.id}): {message_text}')
        answer_chatgpt = await chatgpt_answer(message_text, userid)
        check_tok = check_tokens(userid=userid)
        check_max_tok = check_max_tokens(userid=userid)
        if check_tok:
            await message.answer(check_tok)
        if check_max_tok:
            await message.answer(check_max_tok)
        await message.answer(answer_chatgpt)

    except Exception as e:
        logger.error(f"error in text_handlers.py text_messages: {e}")
        logger.error(type(e))
        await message.answer(LEXICON["something_wrong"])
    finally:
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)
