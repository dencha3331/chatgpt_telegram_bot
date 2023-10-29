from __future__ import annotations
import openai
from openai import OpenAIError
from dataclasses import dataclass

from logs import logger
from config_data import load_config
from services import Checking
from db.async_crud import Crud
from db.models import Dialog, Wallet, Users
from lexicons import LEXICON_RU
from errors import ChatgptAnswerErrors, NegativeBalance, ChangeModel

lexicon: dict[str, str] = LEXICON_RU['user_handlers']

models: dict[str, dict[str, float]] = {
    'gpt-3.5-turbo': {"in": 0.0015, "out": 0.002, "tokens": 3000},
    'gpt-3.5-turbo-16k': {"in": 0.003, "out": 0.004, "tokens": 15000},
    'gpt-4': {"in": 0.03, "out": 0.06, "tokens": 7000},
    'gpt-4-32k': {"in": 0.06, "out": 0.12, "tokens": 31000}
}


@dataclass(frozen=True)
class GptResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


async def chatgpt_for_tg(tg_id: int, text: str | None = None) -> str:
    """
    Getting user data, send current dialog to OpenAi and write processed data to database
    """
    try:
        user: Users = await Crud.get_user_wallet_dialogs(tg_id)
        if not user:
            return "Пройдите регистрацию"
        try:
            dialog: Dialog = [dialog for dialog in user.dialogs if dialog.current_dialog][0]
            if not text:
                text: str = dialog.messages.pop(-1)["content"]
        except IndexError:
            text: str = text
            dialog: Dialog = Dialog(name_chat=text[:20], user=user, messages=[],
                                    model="gpt-3.5-turbo",
                                    wallet=user.wallet, current_dialog=True)
            user.dialogs.append(dialog)
        if not dialog.name_chat:
            dialog.name_chat = text[:20]
        messages: list[dict] = dialog.messages
        messages.append({'role': 'user', 'content': text})
        balance_message: str | None = await _check_balance(user.wallet)
        try:
            token_message: str | None = await _checking_count_max_tokens_in_message(dialog, messages)
        except ChangeModel:
            dialog.messages = messages
            await Crud.save_object(user)
            raise ChangeModel
        chatgpt_response: GptResponse = chatgpt_answer(user.id, messages, dialog.model)
        messages.append({'role': 'assistant', 'content': chatgpt_response.text})
        dialog.messages = messages
        await _calculate_payment(user, chatgpt_response)
        await Crud.save_object(user)
        logger.debug(f'ChatGPT response: {chatgpt_response.text}')
        logger.debug(f"{user.id}:  prompt_tokens: {chatgpt_response.prompt_tokens},"
                     f"completion_tokens: {chatgpt_response.completion_tokens}")
        return "\n".join([str(message) for message in
                          [balance_message, token_message, chatgpt_response.text] if message])
    except NegativeBalance as e:
        return str(e)
    except OpenAIError as e:
        logger.error(f"error in chatgpt.py chatgpt: {e}")
        logger.error(f"type: {type(e)}")
        return str(e)


def chatgpt_answer(name: int | str,
                   message: list[dict] | str,
                   model="gpt-3.5-turbo") -> GptResponse | None:
    """
    Helper function for sending dialog to OpenIai
    """
    try:
        messages: list[dict] = message if type(message) == list \
            else [{'role': 'user', 'content': message}]
        openai.api_key = load_config().open_ai.token  # API openAI
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            user=str(name)
        )
        chatgpt_response: str = completion.choices[0]['message']['content']
        prompt_tokens: int = completion['usage']['prompt_tokens']
        completion_tokens: int = completion['usage']['completion_tokens']
        total_tokens: int = completion['usage']['total_tokens']
        return GptResponse(text=chatgpt_response,
                           prompt_tokens=prompt_tokens,
                           completion_tokens=completion_tokens,
                           total_tokens=total_tokens)
    except Exception as e:
        logger.error(f"error in chatgpt.py chatgpt_answer: {e}")
        raise ChatgptAnswerErrors(str(e))


async def _checking_count_max_tokens_in_message(obj: Dialog,
                                                chat_messages: list[dict]) -> None | str:
    """
    Checking the number of tokens and deleting the first messages if the
    allowed number for sending is exceeded
    """
    print(obj.model)
    if Checking.count_tokens_from_messages(chat_messages) > models[obj.model]["tokens"]:
        if not obj.max_tokens:
            obj.max_tokens = 1
            raise ChangeModel
        elif obj.max_tokens == 1:
            obj.max_tokens = 2
            return """Превышено максимальное количество токенов для отправки сообщения 
                      сообщения будут постепенно удаляться по мере необходимости начиная с первого"""
        while Checking.count_tokens_from_messages(chat_messages) > models[obj.model]["tokens"]:
            chat_messages.pop(0)


async def _calculate_payment(user: Users, message_tokens: GptResponse) -> None:
    """
    Counting money spent
    """
    model: str = [dialog.model for dialog in user.dialogs if dialog.current_dialog][-1]
    wallet: Wallet = user.wallet
    current_balance: float = wallet.balance
    pay: float = await _count_money(model, message_tokens)
    final_balance = current_balance - pay
    wallet.balance = final_balance


async def _count_money(model: str, tokens: GptResponse) -> float:
    """
    Calculating the cost of the current message
    """
    return ((tokens.prompt_tokens / 1000 * models[model]["in"]) +
            (tokens.completion_tokens / 1000 * models[model]["out"]))


async def _check_balance(wallet: Wallet) -> str | None:
    """Check count tokens in send message and check tokens in db on table users"""
    wallet: Wallet = wallet
    if wallet.balance < 0.1:
        return f"Ваш баланс скоро закончиться остаток: {wallet.balance}"
    elif wallet.balance < 0:
        raise NegativeBalance
