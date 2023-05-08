from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicons import LEXICON_RU


def create_inline_kb(width: int, *args: str,
                     last_btn: dict | None = None, **kwargs: str) -> InlineKeyboardMarkup:
    """Generator function to create a InlineKeyboard"""
    LEXICON = LEXICON_RU['buttons']
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


