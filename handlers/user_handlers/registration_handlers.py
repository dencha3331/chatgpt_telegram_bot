from logs import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, Message)

from db import DateBase
from lexicons import LEXICON_RU
from keyboards import create_inline_kb

registration_router: Router = Router()

# User database
TABLE_NAME = "users"
DB_PATH = "db/db_bot.db"

# Variables for cues and buttons
LEXICON: dict[str, str] = LEXICON_RU['registration_handlers']
LEXICON_BTN = LEXICON_RU['buttons']


# StatesGroup-derived class for a group of states
class FSMFillForm(StatesGroup):
    fill_name = State()  # Name
    fill_surname = State()  # Surname
    fill_age = State()  # Age
    fill_gender = State()  # Gender
    fill_wish_news = State()  # Whether to receive news
    fill_update_reg_data = State()  # Registration data update


@registration_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    """Command handler "/cancel" in default state"""
    await message.answer(text=LEXICON['cancel_default_state'])


@registration_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """Handler of "/cancel" command in any states"""
    logger.info(f"Cancel registration user: user id {message.from_user.id}")
    await message.answer(text=LEXICON['cancel_fillform_state'])
    await state.clear()


@registration_router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    """/registration command handler, puts you in the name input state.
    If the user is already registered, it offers to update the data and goes to the state update_reg_data"""
    logger.info(f"Registration user: user_id {message.from_user.id}")
    userid = message.from_user.id
    with DateBase(DB_PATH) as db:
        users_id = db.get_column(table=TABLE_NAME, name_column="user_id")
    if userid not in users_id:
        await state.update_data(user_id=userid)
        await message.answer(text=LEXICON['enter_name'])
        await state.set_state(FSMFillForm.fill_name)
    else:

        markup = create_inline_kb(2, yes_reg_update=LEXICON_BTN['yes'], no_reg_update=LEXICON_BTN['no'])
        await message.answer(text=LEXICON["inline_process_fillform_command_update"],
                             reply_markup=markup)
        await state.set_state(FSMFillForm.fill_update_reg_data)


@registration_router.callback_query(StateFilter(FSMFillForm.fill_update_reg_data),
                                    Text(text=['yes_reg_update', 'no_reg_update']))
async def update_reg_date(callback: CallbackQuery, state: FSMContext):
    """The credential update handler offers a choice of yes or no.
    If accepted, transfers to the name input state, if refused, exits the state machine"""
    if callback.data == 'yes_reg_update':
        await callback.message.edit_text(text=LEXICON['enter_name'])
        await state.set_state(FSMFillForm.fill_name)
    else:
        await callback.answer(LEXICON["update_reg_date_no"])
        await state.clear()


@registration_router.message(StateFilter(FSMFillForm.fill_update_reg_data))
async def negative_update_reg_data(message: Message):
    """Invalid data entry during update"""
    await message.answer(LEXICON["negative_update_reg_data"])


@registration_router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    """Handler of correct input of the name, transfers to the state of input of the surname"""
    await state.update_data(name=message.text)
    await message.answer(text=LEXICON["enter_surname"])

    await state.set_state(FSMFillForm.fill_surname)


@registration_router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    """Invalid name input handler"""
    await message.answer(text=LEXICON["negative_enter_name"])


@registration_router.message(StateFilter(FSMFillForm.fill_surname), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    """Handler for correctly entering a surname, transfers to the state of entering age"""
    await state.update_data(surname=message.text)
    await message.answer(text=LEXICON["enter_age"])

    await state.set_state(FSMFillForm.fill_age)


@registration_router.message(StateFilter(FSMFillForm.fill_surname))
async def warning_not_name(message: Message):
    """Handler for incorrect input of first or last name"""
    await message.answer(text=LEXICON["negative_enter_surname"])


@registration_router.message(StateFilter(FSMFillForm.fill_age),
                             lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    """Age correct input handler, switches to gender selection state"""
    await state.update_data(age=message.text)

    markup = create_inline_kb(2, 'male', 'female', 'undefined_gender')
    await message.answer(text=LEXICON["enter_gender"],
                         reply_markup=markup)
    await state.set_state(FSMFillForm.fill_gender)


@registration_router.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    """Incorrect age input handler"""
    await message.answer(
        text=LEXICON["negative_age"])


@registration_router.callback_query(StateFilter(FSMFillForm.fill_gender),
                                    Text(text=['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    """The handler of the correct input of the selected education and
    transfers to the state of receiving news"""
    await state.update_data(gender=callback.data)

    markup = create_inline_kb(2, 'yes_news', 'no_news')
    await callback.message.edit_text(text=LEXICON["enter_want_news"],
                                     reply_markup=markup)
    await state.set_state(FSMFillForm.fill_wish_news)


@registration_router.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(text=LEXICON["negative_gender"])


@registration_router.callback_query(StateFilter(FSMFillForm.fill_wish_news),
                                    Text(text=['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    """Handler for choosing to receive or not receive news, output from the state machine
    and add to the database"""
    await state.update_data(wish_news=1 if callback.data == 'yes_news' else 0)
    userid = callback.from_user.id
    reg_data = await state.get_data()
    with DateBase(DB_PATH) as db:
        if userid not in db.get_column(table=TABLE_NAME, name_column="user_id"):
            reg_data.update(tokens=100000)
            db.insert(table=TABLE_NAME, column_values=reg_data)
        else:
            db.update_values(table=TABLE_NAME, values=reg_data, params={"user_id": userid})
    await state.clear()
    await callback.message.edit_text(text=LEXICON["end_registration"])
    await callback.message.answer(text=LEXICON["show_data"])


@registration_router.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message: Message):
    """Incorrect input handler when choosing to receive news"""
    await message.answer(text=LEXICON["negative_enter_news"])
