import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from states import PayWMState
from keyboards import CardPriceKB, LinkPayWMKB

payment_router: Router = Router()
payment_state: PayWMState = PayWMState()


@payment_router.callback_query(StateFilter(payment_state.fill_method))
async def process_input_price(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "card":
        keyboard: CardPriceKB = CardPriceKB()
        await state.update_data(card=callback.data)
        await callback.message.edit_text(text=keyboard.text, reply_markup=keyboard.markup)
        # await state.set_state(payment_state.fill_end)
    else:
        await callback.message.edit_text("Введите сумму в долларах.")
    await state.set_state(payment_state.fill_price)


@payment_router.message(StateFilter(payment_state.fill_price))
async def process_enter_price(message: Message, state: FSMContext):
    try:
        price = round(float(message.text), 2)
        await state.update_data(price=price)
        keyboard = LinkPayWMKB()
        # await state.set_state(payment_state.fill_end)
        await message.answer(text=f"{message.from_user.first_name}", reply_markup=keyboard.markup)
        await state.clear()
    except Exception as e:
        print(e)
        await message.answer("Неверный формат. Пример: 1.23")


@payment_router.callback_query(StateFilter(payment_state.fill_price))
async def process_add_price(callback: CallbackQuery, state: FSMContext):
    keyboard = LinkPayWMKB()
    await state.update_data(price=callback.data)
    # await state.set_state(payment_state.fill_end)
    await callback.message.edit_text(text="sdfasfafssfaas",
                                     reply_markup=keyboard.markup)
    await state.clear()
    await asyncio.sleep(5)
    await callback.message.delete()


