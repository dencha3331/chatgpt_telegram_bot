from aiogram import Router, F
from aiogram.filters import Command, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from lexicons import LEXICON_RU

registration_router: Router = Router()

# База данных пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}

# Переменные для реплик и кнопок 
lexicon: dict[str, str] = LEXICON_RU['registration_handlers']
lexicon_buttons: dict[str, str] = LEXICON_RU['registration_handlers']['buttons']


# Класс, наследуемый от StatesGroup, для группы состояний
class FSMFillForm(StatesGroup):

    fill_name = State()  # Состояние ожидания ввода имени
    fill_age = State()  # Состояние ожидания ввода возраста
    fill_gender = State()  # Состояние ожидания выбора пола
    fill_education = State()  # Состояние ожидания выбора образования
    fill_wish_news = State()  # Состояние ожидания выбора получать ли новости


# Хэндлер команды "/cancel" в состоянии по умолчанию 
@registration_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=lexicon['cancel_default_state'])


# Хэндлер команды "/cancel" в любых состояниях
@registration_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):

    await message.answer(text=lexicon['cancel_fillform_state'])
    await state.clear()


# Хэндлер команды /registration, переводит в состояние ввода имени
@registration_router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):

    await message.answer(text=lexicon['enter_name'])
    await state.set_state(FSMFillForm.fill_name)


# Хэндлер корректного ввода имени, переводит в состояние ввода возвраста
@registration_router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):

    await state.update_data(name=message.text)
    await message.answer(text=lexicon["enter_age"])
    
    await state.set_state(FSMFillForm.fill_age)


# Хэндлер некорректного ввода имени
@registration_router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text=lexicon["negative_enter_name"])


# Хэндлер корректного ввода возраста, переводит в состояние выбора пола
@registration_router.message(StateFilter(FSMFillForm.fill_age),
                             lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):

    await state.update_data(age=message.text)

    male_button = InlineKeyboardButton(text=lexicon_buttons['male'],
                                       callback_data='male')
    female_button = InlineKeyboardButton(text=lexicon_buttons['female'],
                                         callback_data='female')
    undefined_button = InlineKeyboardButton(text=lexicon_buttons['undefined_gender'],
                                            callback_data='undefined_gender')

    keyboard: list[list[InlineKeyboardButton]] = [[male_button, female_button],
                                                  [undefined_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text=lexicon["enter_gender"],
                         reply_markup=markup)

    await state.set_state(FSMFillForm.fill_gender)


# Хэндлер некорректного ввода возраста
@registration_router.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text=lexicon["negative_age"])


# Хэндлер нажатия кнопки выбора пола, переводит в состояние образование 
@registration_router.callback_query(StateFilter(FSMFillForm.fill_gender),
                                    Text(text=['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):

    await state.update_data(gender=callback.data)

    secondary_button = InlineKeyboardButton(text=lexicon_buttons['secondary'],
                                            callback_data='secondary')
    higher_button = InlineKeyboardButton(text=lexicon_buttons['higher'],
                                         callback_data='higher')
    no_edu_button = InlineKeyboardButton(text=lexicon_buttons['no_edu'],
                                         callback_data='no_edu')
    
    keyboard: list[list[InlineKeyboardButton]] = [
        [secondary_button, higher_button],
        [no_edu_button]]
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.answer(text=lexicon["enter_education"],
                                  reply_markup=markup)

    
    await state.set_state(FSMFillForm.fill_education)


# Хэндлер некорректного ввода при выборе пола
@registration_router.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(text=lexicon["negative_gender"])


# Хэндлер коретного ввода выбраного образование и переводит в состояние получать новости
@registration_router.callback_query(StateFilter(FSMFillForm.fill_education),
                                    Text(text=['secondary', 'higher', 'no_edu']))
async def process_education_press(callback: CallbackQuery, state: FSMContext)

    await state.update_data(education=callback.data)

    yes_news_button = InlineKeyboardButton(text=lexicon_buttons['yes_news'],
                                           callback_data='yes_news')
    no_news_button = InlineKeyboardButton(text=lexicon_buttons['no_news'],
                                          callback_data='no_news')

    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_news_button,
         no_news_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
 
    await callback.message.edit_text(text=lexicon["enter_want_news"],
                                     reply_markup=markup)
    await state.set_state(FSMFillForm.fill_wish_news)


# Хэндлер некорректного ввода при выборе образования
@registration_router.message(StateFilter(FSMFillForm.fill_education))
async def warning_not_education(message: Message):
    await message.answer(text=lexicon["negative_education"])


# Хэндлер выбора получать или не получать новости и выводить из машины состояний
@registration_router.callback_query(StateFilter(FSMFillForm.fill_wish_news),
                                    Text(text=['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    
    await state.update_data(wish_news=callback.data == 'yes_news')
    
    user_dict[callback.from_user.id] = await state.get_data()
    
    await state.clear()
    
    await callback.message.edit_text(text=lexicon["end_registration"])
    
    await callback.message.answer(text=lexicon["show_data"])


# Хэндлер некорректного ввода при выборе получать новости
@registration_router.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message: Message):
    await message.answer(text=lexicon["negative_enter_news"])


# Хэндлер команды /showdata. Отправляет данные анкеты/отсутствия анкеты
@registration_router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    if message.from_user.id in user_dict:
        await message.answer(text=f'{lexicon["show_db_name"]}: {user_dict[message.from_user.id]["name"]}\n'
                                  f'{lexicon["show_db_age"]}: {user_dict[message.from_user.id]["age"]}\n'
                                  f'{lexicon["show_db_gender"]}: {user_dict[message.from_user.id]["gender"]}\n'
                                  f'{lexicon["show_db_education"]}: {user_dict[message.from_user.id]["education"]}\n'
                                  f'{lexicon["show_db_news"]}: {user_dict[message.from_user.id]["wish_news"]}')
    else:
        await message.answer(text=lexicon["empty_db"])

