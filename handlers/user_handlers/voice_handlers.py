from aiogram import Router, F
from aiogram.types import Message

from logs import logger
from config_data import bot
from lexicons import LEXICON_RU
from services import (process_voice_message,
                      check_tokens,
                      chatgpt_answer)

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
voice_router: Router = Router()


@voice_router.message(F.voice)
async def voice(message: Message):
    """
    Voice message translate to text with VOSK and send chatgpt_answer() on chatgpt.py
    """
    processing_message = await message.reply(LEXICON['processing_message'])
    try:
        user_id = message.from_user.id
        file_id = message.voice.file_id
        file_path = await bot.get_file(file_id)
        file_data = await bot.download_file(file_path.file_path)
        file_bin = file_data.read()
        voice_to_text = await process_voice_message(file_bin)
        if voice_to_text:
            await message.reply(voice_to_text)
            answer_chatgpt = await chatgpt_answer(voice_to_text, user_id)
            check_tok = await check_tokens(userid=user_id)
            if check_tok:
                await message.answer(check_tok)
            await message.answer(answer_chatgpt)
        else:
            await message.answer(LEXICON["something_wrong"])
    except Exception as e:
        await message.answer(LEXICON["something_wrong"])
        logger.error(e)
    finally:
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)