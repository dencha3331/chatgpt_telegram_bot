from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from db.async_crud import Crud
from db.models import Users
from keyboards import KeyboardProcessFillFormUpdate, KeyboardChosePayMethod
from states import FSMRegistrationFillForm, PayWMState
from logs import logger
from lexicons import LEXICON_RU
from services import Checking
from errors import MessageFromUserIsNone, UserNotRegistration


LEXICON: dict[str, str] = LEXICON_RU['user_handlers']
command_router: Router = Router()
registration_state: FSMRegistrationFillForm = FSMRegistrationFillForm()
payment_state: PayWMState = PayWMState()


@command_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message) -> None:
    """Command handler "/cancel" in default state"""
    await message.answer(text=LEXICON['cancel_default_state'])


@command_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext) -> None:
    """Handler of "/cancel" command in any states"""
    logger.info(f"Cancel registration user: user id "
                f"{message.from_user.id or 'unknown'}")
    await message.answer(text=LEXICON['cancel_fill_form_state'])
    await state.clear()


@command_router.message(CommandStart())
async def welcome_command(message: Message) -> None:
    """ Command /start send start message """
    name = message.from_user.first_name or ""
    userid = message.from_user.id or ""
    logger.info(f"start chat for {name}({userid})")
    await message.answer(f"{name}!\n{LEXICON['/start']}")


@command_router.message(Command(commands=['help']))
async def help_command(message: Message) -> None:
    """ Command /help send help message """
    await message.reply(LEXICON["/help"])


@command_router.message(Command(commands=["new"]))
async def new_dialog(message: Message) -> None:
    """ Command /new makes the list messages[userid] empty """
    try:
        await Checking.check_message_from_user_not_none(message)
        reset_message_chat: str = await Crud.new_dialog(message.from_user.id)
        await message.answer(reset_message_chat)
        logger.info(f"Начат новый диалог с {message.from_user.first_name}")
    except MessageFromUserIsNone as e:
        logger.error(e)
    except Exception as e:
        logger.error(f"new dialog command error: {e}")
        await message.answer(LEXICON["something_wrong"])


@command_router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fill_form_command(message: Message, state: FSMContext) -> None:
    """/registration command handler, puts you in the name input state.
    If the user is already registered, it offers to update the data and
     goes to the state update_reg_data"""
    try:
        await Checking.check_message_from_user_not_none(message)
        userid: int = message.from_user.id
        logger.info(f"Registration user: user_id {userid}")

        users_id = await Crud.select_column(Users.id)
        if userid not in users_id:
            await state.update_data(id=userid)
            await message.answer(text=LEXICON['enter_name'])
            await state.set_state(registration_state.fill_name)
        else:
            keyboard = KeyboardProcessFillFormUpdate()
            await message.answer(text=keyboard.text,
                                 reply_markup=keyboard.markup)
            await state.set_state(registration_state.fill_update_reg_data)
    except MessageFromUserIsNone:
        pass


@command_router.message(Command(commands='showdata'))
async def process_showdata_command(message: Message) -> None:
    """ Command "/showdata send user profile or empty profile """
    try:
        await Checking.check_message_from_user_not_none(message)
        user_data: str = await Crud.get_user_data_from_db(message.from_user.id)
        await message.answer(user_data)
        logger.debug(f"Get data from db user: {message.from_user.first_name}({message.from_user.id})")
    except MessageFromUserIsNone as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)


@command_router.message(Command(commands="pay"), StateFilter(default_state))
async def pay_wm(message: Message, state: FSMContext) -> None:
    """Call payment"""
    try:
        await Checking.check_message_from_user_not_none(message)
        userid: int = message.from_user.id
        logger.info(f"Start payment: user_id {userid}")

        await Checking.check_user_not_in_db(message)
        await state.update_data(user_id=userid)
        keyboard = KeyboardChosePayMethod()
        await message.answer(text=keyboard.text,
                             reply_markup=keyboard.markup)
        await state.set_state(payment_state.fill_method)

    except (MessageFromUserIsNone, UserNotRegistration):
        pass


@command_router.message(Command(commands="webapp"))
async def webapp(message: Message):
    pass
