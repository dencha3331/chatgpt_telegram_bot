from aiogram import Router, F
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from lexicons import LEXICON_RU
from states import FSMRegistrationFillForm
from services import WorkingDb
from keyboards import (KeyboardWontNews,
                       KeyboardEnterGender, )

# Variables for cues and buttons
LEXICON: dict[str, str] = LEXICON_RU['registration_handlers']
LEXICON_BTN: dict[str, str] = LEXICON_RU['buttons']
registration_router: Router = Router()
registration_state: FSMRegistrationFillForm = FSMRegistrationFillForm()


@registration_router.callback_query(StateFilter(registration_state.fill_update_reg_data),
                                    Text(text=['yes_reg_update', 'no_reg_update']))
async def update_reg_date(callback: CallbackQuery, state: FSMContext) -> None:
    """The credential update handler offers a choice of yes or no.
    If accepted, transfers to the name input state, if refused, exits the state machine"""
    if callback.data == 'yes_reg_update':
        await callback.message.edit_text(text=LEXICON['enter_name'])
        await state.set_state(registration_state.fill_name)
    else:
        await callback.message.edit_text(LEXICON["update_reg_date_no"])
        await state.clear()


@registration_router.message(StateFilter(registration_state.fill_update_reg_data))
async def negative_update_reg_data(message: Message) -> None:
    """Invalid data entry during update"""
    await message.answer(LEXICON["negative_update_reg_data"])


@registration_router.message(StateFilter(registration_state.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext) -> None:
    """Handler of correct input of the name, transfers to the state of input of the surname"""
    await state.update_data(name=message.text)
    await message.answer(text=LEXICON["enter_surname"])
    await state.set_state(registration_state.fill_surname)


@registration_router.message(StateFilter(registration_state.fill_name))
async def warning_not_correct_name(message: Message) -> None:
    """Invalid name input handler"""
    await message.answer(text=LEXICON["negative_enter_name"])


@registration_router.message(StateFilter(registration_state.fill_surname), F.text.isalpha())
async def process_surname_sent(message: Message, state: FSMContext) -> None:
    """Handler for correctly entering a surname, transfers to the state of entering age"""
    await state.update_data(surname=message.text)
    await message.answer(text=LEXICON["enter_age"])
    await state.set_state(registration_state.fill_age)


@registration_router.message(StateFilter(registration_state.fill_surname))
async def warning_not_correct_surname(message: Message) -> None:
    """Handler for incorrect input of first or last name"""
    await message.answer(text=LEXICON["negative_enter_surname"])


@registration_router.message(StateFilter(registration_state.fill_age),
                             lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext) -> None:
    """Age correct input handler, switches to gender selection state"""
    await state.update_data(age=message.text)
    keyboard = KeyboardEnterGender()
    await message.answer(text=keyboard.text,
                         reply_markup=keyboard.markup)
    await state.set_state(registration_state.fill_gender)


@registration_router.message(StateFilter(registration_state.fill_age))
async def warning_not_correct_age(message: Message) -> None:
    """Incorrect age input handler"""
    await message.answer(
        text=LEXICON["negative_age"])


@registration_router.callback_query(StateFilter(registration_state.fill_gender),
                                    Text(text=['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext) -> None:
    """The handler of the correct input of the selected education and
    transfers to the state of receiving news"""
    await state.update_data(gender=callback.data)
    keyboard = KeyboardWontNews()
    await callback.message.edit_text(text=keyboard.text,
                                     reply_markup=keyboard.markup)
    await state.set_state(registration_state.fill_wish_news)


@registration_router.message(StateFilter(registration_state.fill_gender))
async def warning_not_correct_gender(message: Message) -> None:
    await message.answer(text=LEXICON["negative_gender"])


@registration_router.callback_query(StateFilter(registration_state.fill_wish_news),
                                    Text(text=['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext) -> None:
    """Handler for choosing to receive or not receive news, output from the state machine
    and add to the database"""
    await state.update_data(wish_news=1 if callback.data == 'yes_news' else 0)
    userid = callback.from_user.id
    reg_data = await state.get_data()
    WorkingDb.save_user_registration_data_in_db(userid, reg_data)
    await state.clear()
    await callback.message.edit_text(text=LEXICON["end_registration"])
    await callback.message.answer(text=LEXICON["show_data"])


@registration_router.message(StateFilter(registration_state.fill_wish_news))
async def warning_not_correct_wish_news(message: Message) -> None:
    """Incorrect input handler when choosing to receive news"""
    await message.answer(text=LEXICON["negative_enter_news"])
