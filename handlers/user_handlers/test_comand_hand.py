from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from db.async_crud import Crud

import keyboards
from states import FSMRegistrationFillForm, PayWMState, CommandState
from logs import logger
from lexicons import LEXICON_RU
from errors import MessageFromUserIsNone, UserNotRegistration
from filters import ChoiceDialogFilter

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
command_router: Router = Router()
command_state: CommandState = CommandState()
registration_state: FSMRegistrationFillForm = FSMRegistrationFillForm()
payment_state: PayWMState = PayWMState()


@command_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message) -> None:
    """Command handler "/cancel" in default state"""
    await message.delete()
    await message.answer(text=LEXICON['cancel_default_state'])


@command_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext) -> None:
    """Handler of "/cancel" command in any states"""
    logger.info(f"Cancel registration user: user id "
                f"{message.from_user.id or 'unknown'}")
    await message.delete()
    await message.answer(text=LEXICON['cancel_fill_form_state'])
    await state.clear()


@command_router.message(CommandStart())
async def welcome_command(message: Message) -> None:
    """ Command /start send start message """
    await message.delete()
    name = message.from_user.first_name or ""
    userid = message.from_user.id or ""
    logger.info(f"start chat for {name}({userid})")
    await message.answer(f"{name}!\n{LEXICON['/start']}")


@command_router.message(Command(commands=['help']))
async def help_command(message: Message) -> None:
    """ Command /help send help message """
    await message.delete()
    await message.reply(LEXICON["/help"])


@command_router.message(Command(commands=["new"]))
async def clear_dialog(message: Message) -> None:
    """ Command /new makes the list messages[userid] empty """
    await message.delete()
    try:
        userid: int = message.from_user.id
        reset_message_chat: str = await Crud.clear_dialog(userid)
        await message.answer(reset_message_chat)
        logger.info(f"Почистил диалог с {message.from_user.first_name}")
    except Exception as e:
        logger.error(f"new dialog command error: {e}")
        await message.answer(LEXICON["something_wrong"])


@command_router.message(Command(commands=["new_dial"]))
async def new_dialog(message: Message) -> None:
    """ Command /new makes the list messages[userid] empty """
    await message.delete()
    try:
        userid: int = message.from_user.id
        reset_message_chat: str = await Crud.new_dialog(userid)
        await message.answer(reset_message_chat)
        logger.info(f"Почистил диалог с {message.from_user.first_name}")
    except Exception as e:
        logger.error(f"new dialog command error: {e}")
        await message.answer(LEXICON["something_wrong"])


@command_router.message(Command(commands=["all_dial"]), StateFilter(default_state))
async def choice_dial(message: Message, state: FSMContext) -> None:
    await message.delete()
    userid: int = message.from_user.id
    markup: InlineKeyboardMarkup = await keyboards.ChoiceDialogKeyboard(userid)()
    await message.answer(text="Выберите диалог", reply_markup=markup)
    await state.set_state(command_state.choice_dial)


@command_router.callback_query(StateFilter(command_state.choice_dial), ChoiceDialogFilter())
async def change_or_leave_dialog(callback: CallbackQuery, choice_message: str, state: FSMContext) -> None:
    message: str = choice_message
    await callback.message.delete()
    if message == "no_choice":
        await callback.message.answer("Продолжаем с того же места")
    else:
        await callback.message.answer(f"Сменил диалог на: {message}")
    await state.clear()


@command_router.callback_query(StateFilter(command_state.choice_dial))
async def negative_input_choice_dial(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer("Выберете из списка или нажмите /cancel")


@command_router.message(Command(commands=["delete_all_dialogs"]), StateFilter(default_state))
async def delete_all_dialogs(message: Message, state: FSMContext) -> None:
    await message.delete()
    keyboard = keyboards.ConfirmDeleteAllDialogsKeyboard()
    await message.answer(text=keyboard.text, reply_markup=keyboard.markup)
    await state.set_state(command_state.delete_all_dialogs)


@command_router.callback_query(StateFilter(command_state.delete_all_dialogs))
async def confirmed_delete_all_dialogs(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    userid: int = callback.from_user.id
    data: str = callback.data
    if data == "yes":
        await Crud.delete_all_dialogs(userid=userid)
        await callback.message.answer("Удалил. Начнем с чистого листа")
    else:
        await callback.message.answer("Нечего не удаляю")
    await state.clear()


@command_router.message(Command(commands=["show_balance"]))
async def show_balance(message: Message) -> None:
    await message.delete()
    userid: int = message.from_user.id
    balance: str = await Crud.show_balance(userid)
    await message.answer(balance)


@command_router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fill_form_command(message: Message, state: FSMContext) -> None:
    """/registration command handler, puts you in the name input state.
    If the user is already registered, it offers to update the data and
     goes to the state update_reg_data"""
    # try:
    await message.delete()
    userid: int = message.from_user.id
    logger.debug(f"Registration user: user_id {userid}")

    users_id = await Crud.get_user(userid)
    if not users_id:
        await state.update_data(id=userid)
        await message.answer(text=LEXICON['enter_name'])
        await state.set_state(registration_state.fill_name)
    else:
        keyboard = keyboards.KeyboardProcessFillUserFormUpdate()
        await message.answer(text=keyboard.text,
                             reply_markup=keyboard.markup)
        await state.set_state(registration_state.fill_update_reg_data)
    # except Exception as e:
    #     logger.error(f"Error in process_fill_form_command: {e}")


@command_router.message(Command(commands='showdata'))
async def process_showdata_command(message: Message) -> None:
    """ Command "/showdata send user profile or empty profile """
    await message.delete()
    try:
        userid: int = message.from_user.id
        user_data: str = await Crud.get_user_data_from_db(userid)
        await message.answer(user_data)
        logger.debug(f"Get data from db user: {message.from_user.first_name}({message.from_user.id})")
    except Exception as e:
        logger.error(e)


@command_router.message(Command(commands="pay"), StateFilter(default_state))
async def pay_wm(message: Message, state: FSMContext) -> None:
    """Call payment"""
    await message.delete()
    try:
        # await Checking.check_message_from_user_not_none(message)
        userid: int = message.from_user.id
        logger.info(f"Start payment: user_id {userid}")

        # await Checking.check_user_not_in_db(message)
        await state.update_data(user_id=userid)
        keyboard = keyboards.KeyboardChosePayMethod()
        await message.answer(text=keyboard.text,
                             reply_markup=keyboard.markup)
        await state.set_state(payment_state.fill_method)

    except (MessageFromUserIsNone, UserNotRegistration):
        pass


# @command_router.message(Command(commands="webapp"))
# async def webapp(message: Message):
#     pass
