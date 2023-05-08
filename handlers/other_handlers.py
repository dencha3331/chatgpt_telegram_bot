from aiogram.types import Message
from aiogram import Router

from lexicons import LEXICON_RU

lexicon = LEXICON_RU["user_handlers"]
other_router: Router = Router()


@other_router.message()
async def unknown_message(message: Message):
    """If not one handler didn't work"""
    await message.answer(lexicon['unknown_message'])
