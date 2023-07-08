from dataclasses import dataclass
from aiogram.types import InlineKeyboardMarkup

from keyboards import create_inline_callback_data_kb
from lexicons import LEXICON_RU

LEXICON: dict[str, str] = LEXICON_RU['registration_handlers']
LEXICON_BTN = LEXICON_RU['buttons']


# _______________registration_handlers.py___________________
@dataclass(frozen=True)
class KeyboardProcessFillFormUpdate:
    text: str = LEXICON["inline_process_fill_form_command_update"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, yes_reg_update=LEXICON_BTN['yes'],
                                                                  no_reg_update=LEXICON_BTN['no'])


@dataclass(frozen=True)
class KeyboardEnterGender:
    text: str = LEXICON["enter_gender"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, 'male', 'female', 'undefined_gender')


@dataclass(frozen=True)
class KeyboardWontNews:
    text: str = LEXICON["enter_want_news"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, 'yes_news', 'no_news')


# _______________

# _____________________voice_handlers.py___________________
@dataclass()
class KeyboardCorrectText:
    text: str
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, "yes", "no")
