from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logs import logger

from lexicons import LEXICON_RU

LEXICON: dict[str, str] = LEXICON_RU['buttons']
models: dict[str, dict[str, float]] = {
    'gpt-3.5-turbo': {"in": 0.0015, "out": 0.002, "tokens": 3000},
    'gpt-3.5-turbo-16k': {"in": 0.003, "out": 0.004, "tokens": 15000},
    'gpt-4': {"in": 0.03, "out": 0.06, "tokens": 7000},
    'gpt-4-32k': {"in": 0.06, "out": 0.12, "tokens": 31000}
}


def create_inline_callback_data_kb(width: int,
                                   *args: str,
                                   last_btn: dict | None = None,
                                   **kwargs: str) -> InlineKeyboardMarkup:
    # try:
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
        for button, text in last_btn.items():
            kb_builder.row(InlineKeyboardButton(text=text, callback_data=button))

    return kb_builder.as_markup()
    # except Exception as e:
    #     logger.error(f"error in inline_kb.py create_inline_kb: {e}")
    #     logger.error(f"{type(e)}")
