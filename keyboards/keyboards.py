from dataclasses import dataclass
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import create_inline_callback_data_kb
from lexicons import LEXICON_RU

LEXICON: dict[str, str] = LEXICON_RU['registration_handlers']
LEXICON_BTN = LEXICON_RU['buttons']
LEXICON_PAY_WM = LEXICON_RU['payment_wm']


# _______________registration_handlers.py___________________
@dataclass
class KeyboardProcessFillFormUpdate:
    text: str = LEXICON["inline_process_fill_form_command_update"]
    markup = create_inline_callback_data_kb(2, yes_reg_update=LEXICON_BTN['yes'],
                                                                  no_reg_update=LEXICON_BTN['no'])



class KeyboardEnterGender:
    text: str = LEXICON["enter_gender"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, 'male', 'female', 'undefined_gender')



class KeyboardWontNews:
    text: str = LEXICON["enter_want_news"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, 'yes_news', 'no_news')



class KeyboardChosePayMethod:
    text: str = LEXICON["chose_payment_method"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, card=LEXICON_BTN["card"],
                                                                  wm_wallet=LEXICON_BTN["wm_wallet"])


# _____________________paymentWM.py________________________

def web_app_keyboard():  # создание клавиатуры с webapp кнопкой
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    web_app = WebAppInfo(url="https://cherydeni.ru/paywm")  # создаем webappinfo - формат хранения url
    button = InlineKeyboardButton(text="Перейти к оплате", url="https://cherydeni.ru/paywm")
    # button = InlineKeyboardButton(text="Перейти к оплате", url="http://127.0.0.1:8000")
    kb_builder.row(button, width=1)
    return kb_builder.as_markup()



class CardPriceKB:
    text: str = LEXICON_PAY_WM["chose_price"]
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, five="5$", ten="10$",
                                                                  fifteen="15$", twenty="20$")


@dataclass
class LinkPayWMKB:
    text: str = "Преступить к оплате"
    markup = web_app_keyboard()


# _____________________voice_handlers.py___________________

class KeyboardCorrectText:
    text: str
    markup: InlineKeyboardMarkup = create_inline_callback_data_kb(2, "yes", "no")
