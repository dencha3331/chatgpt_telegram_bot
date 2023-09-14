from __future__ import annotations
import openai
from dataclasses import dataclass

from logs import logger
from config_data import load_config
from services import Checking
from db.async_crud import Crud
from db.models import Dialog, Wallet
from lexicons import LEXICON_RU
from errors import ChatgptAnswerErrors

lexicon: dict[str, str] = LEXICON_RU['user_handlers']


@dataclass(frozen=True)
class GptResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


async def chatgpt(name: int | str, text: str,
                  model="gpt-3.5-turbo") -> str:
    """
    Interaction with gpt, saves messages
    to the database, calculates the balance of tokens
    and saves their number to the 'users' table
    return string response from chatGPT or exception string
    """
    try:
        user_name: int | str = name
        user_message: str = text
        openai.api_key = load_config().open_ai.token  # API openAI
        messages: list[dict] = await _get_messages_from_db(user_name)
        if not messages:
            pass
        messages.append({'role': 'user', 'content': user_message})
        await _checking_count_max_tokens_in_message(user_name, messages)
        chatgpt_response: GptResponse = chatgpt_answer(user_name, user_message,
                                                       messages, model)
        messages.append({'role': 'assistant', 'content': chatgpt_response.text})
        await _save_data_messages_in_db(user_name, messages, chatgpt_response)
        logger.info(f'ChatGPT response: {chatgpt_response.text}')
        logger.info(f"{user_name}: Total tokens: {chatgpt_response.total_tokens}")

        return chatgpt_response.text

    except Exception as e:
        logger.error(f"error in chatgpt.py chatgpt: {e}")
        logger.error(f"type: {type(e)}")
        return lexicon['something_wrong']


def chatgpt_answer(name: int | str,
                   text: str,
                   messages: list[dict] | None = None,
                   model="gpt-4") -> GptResponse | None:
    try:
        messages: list[dict] = messages or []
        messages.append({'role': 'user', 'content': text})
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


async def _get_messages_from_db(user_name: str | int) -> list[dict]:
    return await Crud.select_cell(Dialog.messages, user_id=user_name)


async def _checking_count_max_tokens_in_message(user_name: int | str, chat_messages: list[dict],
                                                count: int = 3000, model="gpt-3.5-turbo"):
    if Checking.count_tokens_from_messages(chat_messages, model) > count:
        if not await Crud.select_cell(Dialog.max_tokens, user_id=user_name):
            await Crud.update(Dialog(max_tokens=1), user_id=user_name)
        while Checking.count_tokens_from_messages(chat_messages, model) > count:
            chat_messages.pop(0)


async def _save_data_messages_in_db(user_name: int | str, chat_messages: list[dict],
                                    message_tokens: GptResponse) -> None:
    current_balance: float = await Crud.select_cell(Wallet.balance, users_id=user_name)
    model: str = await Crud.select_cell(Dialog.model, user_id=user_name)
    pay: float = await count_money(model, message_tokens)
    final_balance = current_balance - pay
    name_chat: str = chat_messages[-1]['content'][:20]
    if not await Crud.select_cell(Dialog.name_chat, user_id=user_name,
                                  current_dialog=True):
        await call_name_dialog(user_name, name_chat)
    await Crud.update(Dialog(messages=chat_messages), user_id=user_name)
    await Crud.update(Wallet(balance=final_balance), user_id=user_name)


async def count_money(model: str, tokens: GptResponse) -> float:
    return (tokens.prompt_tokens / 1000 * 0.0015) + (tokens.completion_tokens / 1000 * 0.003)


async def call_name_dialog(userid, name):
    await Crud.update(Dialog(name_chat=name), user_id=userid, current_dialog=True)

