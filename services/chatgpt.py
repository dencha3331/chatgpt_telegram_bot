from __future__ import annotations
import json
import openai
from dataclasses import dataclass

from logs import logger
from config_data import load_config
from services import Checking
from db import DateBase
from lexicons import LEXICON_RU
from errors import ChatgptAnswerErrors

lexicon: dict[str, str] = LEXICON_RU['user_handlers']
DB_PATH = "db/db_bot.db"


@dataclass(frozen=True)
class GptResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


async def chatgpt(name: int | str, text: str,
                  model="gpt-3.5-turbo") -> str:
    """
    Interaction with gpt3.5-turbo, saves messages
    to the database, calculates the balance of tokens
    and saves their number to the 'users' table
    return string response from chatGPT or exception string
    """
    try:
        user_name: int | str = name
        user_message: str = text
        openai.api_key = load_config().open_ai.token  # API openAI
        messages: list[dict] = _get_messages_from_db(user_name)
        messages.append({'role': 'user', 'content': user_message})
        _checking_count_max_tokens_in_message(user_name, messages)
        chatgpt_response: GptResponse = chatgpt_answer(user_name, user_message,
                                                       messages, model)
        messages.append({'role': 'assistant', 'content': chatgpt_response.text})
        message_tokens: int = chatgpt_response.total_tokens
        _save_data_messages_in_db(user_name, messages, message_tokens)
        # logger.debug(f'{message.from_user.first_name}({message.from_user.id}): {message_text}')
        logger.info(f'ChatGPT response: {chatgpt_response.text}')
        logger.info(f"{user_name}: Total tokens: {message_tokens}")

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
        if messages is None:
            messages = []
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


def _get_messages_from_db(user_name: str | int) -> list[dict]:
    with DateBase(DB_PATH) as db:
        messages: str = db.get_cell_value("messages_chatgpt",
                                          "messages", ("user_id", user_name))
    return json.loads(messages)


def _checking_count_max_tokens_in_message(user_name: int | str,
                                          chat_messages: list[dict], model="gpt-3.5-turbo"):
    with DateBase(DB_PATH) as db:
        if Checking.count_tokens_from_messages(chat_messages, model) > 3000:
            if not db.get_cell_value("messages_chatgpt",
                                     "max_tokens", ("user_id", user_name,)):
                db.update_values("messages_chatgpt", {"max_tokens": 1},
                                 {"user_id": user_name})
            while Checking.count_tokens_from_messages(chat_messages, model) > 3000:
                chat_messages.pop(0)


def _save_data_messages_in_db(user_name: int | str, chat_messages: list[dict],
                              message_tokens: int) -> None:
    with DateBase(DB_PATH) as db:
        str_chat_messages: str = json.dumps(chat_messages)
        current_tokens: int = db.get_cell_value("messages_chatgpt", "tokens",
                                                ("user_id", user_name))
        total_tokens: int = current_tokens - message_tokens
        db.update_values("messages_chatgpt",
                         {"messages": str_chat_messages,
                          "tokens": total_tokens},
                         {"user_id": user_name})
