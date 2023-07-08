from typing import BinaryIO
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, File, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state

from keyboards import create_inline_callback_data_kb
from logs import logger
from config_data import bot
from lexicons import LEXICON_RU
from errors import UserNotRegistration
from states import VoiceState
from services import process_voice_to_text, Checking, chatgpt

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
voice_router: Router = Router()


@voice_router.message(F.voice, StateFilter(default_state))
async def voice(message: Message, state: FSMContext):
    """
    Voice message translate to text with VOSK and send chatgpt_answer() on chatgpt.py
    """
    processing_message = await message.reply(LEXICON['processing_message'])
    try:
        await Checking.check_user_not_in_db(message)
        file_bin: bytes = await get_voice_from_bytes(message)
        voice_to_text: str = await process_voice_to_text(file_bin)
        await message.answer(text=f"\tВсе верно?\n{voice_to_text}",
                             reply_markup=create_inline_callback_data_kb(2, "yes", "no"))
        await state.set_state(VoiceState.correct_text)

    except UserNotRegistration:
        pass
    except Exception as e:
        await message.answer(LEXICON["something_wrong"])
        logger.error(f"error in voice_handlers.py voice: {e}")
        logger.error(type(e))
    finally:
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)


@voice_router.callback_query(StateFilter(VoiceState.correct_text))
async def process_correct_text(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == "yes":
        processing_message = await callback.message.edit_text(LEXICON['processing_message'])
        try:
            text: str = callback.message.text.split("\n")[1]
            answer_chatgpt = await chatgpt(user_id, text)
            logger.info(f"{callback.from_user.id}, {callback.message.from_user.id}, {callback.message.text}")
            logger.info(f"{text}, {user_id}")
            await Checking.check_tokens(callback)
            await callback.message.edit_text(answer_chatgpt)
            await state.clear()
        except Exception as e:
            await bot.delete_message(chat_id=processing_message.chat.id,
                                     message_id=processing_message.message_id)
            logger.info(f"Error in voice_handler.py process_correct_text: {e}")
    elif callback.data == "no":
        await callback.message.edit_text("отправьте повторно")
        await state.clear()


async def get_voice_from_bytes(message: Message) -> bytes:
    file_id: str = message.voice.file_id
    file_path: File = await bot.get_file(file_id)
    file_data: BinaryIO = await bot.download_file(file_path.file_path)
    return file_data.read()
