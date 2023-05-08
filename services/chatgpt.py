import json
import openai

from logs import logger
from config_data import load_config
from services import count_tokens_from_messages
from db import DateBase
from lexicons import LEXICON_RU

lexicon: dict[str, str] = LEXICON_RU['user_handlers']


async def chatgpt_answer(user_message: str, userid: int) -> str:
    """
    Interaction with gpt3.5-turbo, saves messages to the database, calculates the balance of tokens
    and saves their number to the 'users' table
    return string response from chatGPT or exception string
    """
    DB_PATH = "db/db_bot.db"
    openai.api_key = load_config().open_ai.token  # API openAI
    with DateBase(DB_PATH) as db:
        try:
            model = "gpt-3.5-turbo-0301"
            if userid not in db.get_column("users", "user_id"):
                return "Пройдите регистрацию"
            chat_messages = json.loads(db.get_cell_value("messages_chatgpt", "messages", ("user_id", userid)))
            chat_messages.append({'role': 'user', 'content': user_message})
            if count_tokens_from_messages(chat_messages, model) > 3000:
                if not db.get_cell_value("messages_chatgpt", "max_tokens", ("user_id", userid,)):
                    db.update_values("messages_chatgpt", {"max_tokens": 1}, {"user_id": userid})
                while count_tokens_from_messages(chat_messages, model) > 2000:
                    chat_messages.pop(0)
            completion = openai.ChatCompletion.create(
                model=model,
                messages=chat_messages,
                max_tokens=1024,
                temperature=0.7,
                frequency_penalty=0,
                presence_penalty=0,
                user=str(userid)
            )
            chatgpt_response = completion.choices[0]['message']
            chat_messages.append({'role': 'assistant', 'content': chatgpt_response['content']})
            str_chat_messages = json.dumps(chat_messages)
            current_tokens = db.get_cell_value("messages_chatgpt", "tokens", ("user_id", userid))
            message_tokens = completion['usage']['total_tokens']
            total_tokens = current_tokens - message_tokens
            db.update_values("messages_chatgpt", {"messages": str_chat_messages,
                                                  "tokens": total_tokens}, {"user_id": userid})
            logger.debug(f'ChatGPT response: {chatgpt_response["content"]}')
            logger.info(f'{userid}:\nTotal tokens: {completion["usage"]["total_tokens"]}')

            return chatgpt_response['content']

        except Exception as e:
            logger.error(f"error in answer: {e}")
            logger.error(f"type: {type(e)}")
            return lexicon['something_wrong']

