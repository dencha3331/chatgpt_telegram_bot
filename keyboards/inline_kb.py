from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logs import logger

from lexicons import LEXICON_RU

LEXICON: dict[str, str] = LEXICON_RU['buttons']


def create_inline_kb(width: int, *args: str,
                     last_btn: dict | None = None, **kwargs: str) -> InlineKeyboardMarkup:
    try:
        """Generator function to create a InlineKeyboard"""
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        buttons: list[InlineKeyboardButton] = []
        if args:
            for button in args:
                buttons.append(InlineKeyboardButton(text=LEXICON[button] if button in LEXICON else button,
                                                    callback_data=button))
        if kwargs:
            for button, text in kwargs.items():
                buttons.append(InlineKeyboardButton(text=text, callback_data=button))

        kb_builder.row(*buttons, width=width)
        if last_btn:
            for button, text in last_btn:
                kb_builder.row(InlineKeyboardButton(text=text, callback_data=button))

        return kb_builder.as_markup()
    except Exception as e:
        logger.error(f"error in inline_kb.py create_inline_kb: {e}")
        logger.error(f"{type(e)}")
