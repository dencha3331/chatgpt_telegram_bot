from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import TextHandChangeOrLeaveModel
from logs import logger
from config_data import bot
from lexicons import LEXICON_RU
from errors import ChangeModel
from services import chatgpt_for_tg
from keyboards import ChangeModelOverflowKeyboard
from db import Crud

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
text_router: Router = Router()
models: dict[str, dict[str, float]] = {
    'gpt-3.5-turbo': {"in": 0.0015, "out": 0.002, "tokens": 3000},
    'gpt-3.5-turbo-16k': {"in": 0.003, "out": 0.004, "tokens": 15000},
    'gpt-4': {"in": 0.03, "out": 0.06, "tokens": 7000},
    'gpt-4-32k': {"in": 0.06, "out": 0.12, "tokens": 31000}
}


@text_router.message(F.text)
async def text_messages(message: Message, state: FSMContext) -> None:
    """
    Handles all text message and send chatgpt_answer() in chatgpt.py
    """
    processing_message = await message.reply(LEXICON['processing_message'])
    try:
        userid: int = message.from_user.id
        answer_chatgpt: str = await chatgpt_for_tg(userid, message.text)
        await message.answer(answer_chatgpt)
        logger.debug(f'{message.from_user.first_name}'
                     f'({message.from_user.id}): {message.text}')
    except ChangeModel:
        keyboard = ChangeModelOverflowKeyboard()
        await message.answer(text=keyboard.text,
                             reply_markup=keyboard.markup)
        await state.set_state(TextHandChangeOrLeaveModel.change_model)
    # except Exception as e:
    #     logger.error(f"error in text_handlers.py text_messages: {e}")
    #     logger.error(type(e))
    #     await message.answer(LEXICON["something_wrong"])
    finally:
        await bot.delete_message(chat_id=processing_message.chat.id,
                                 message_id=processing_message.message_id)


@text_router.callback_query(StateFilter(TextHandChangeOrLeaveModel.change_model))
async def change_or_leave_model(callback: CallbackQuery, state: FSMContext) -> None:
    userid: int = callback.from_user.id
    model: str = callback.data
    if model != "no_change":
        await Crud.change_or_leave_model(userid, model)
    answer_chatgpt: str = await chatgpt_for_tg(userid)
    await callback.message.delete()
    await callback.answer(answer_chatgpt)
    await state.clear()
