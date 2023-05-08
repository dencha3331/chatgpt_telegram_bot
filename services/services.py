import tiktoken

from db import DateBase
from lexicons import LEXICON_RU

DB_PATH = "db/db_bot.db"
lexicon = LEXICON_RU['service']


def count_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")


async def check_tokens(userid: int):
    """Check count tokens in send message and check tokens in db on table users"""
    with DateBase(DB_PATH) as db:
        tokens = db.get_cell_value("messages_chatgpt", "tokens", ("user_id", userid))
        max_tokens = db.get_cell_value("messages_chatgpt", "max_tokens", ("user_id", userid,))
        if tokens < 10000:
            return f"У вас осталось {tokens} токенов"
        if max_tokens == 1:
            db.update_values("messages_chatgpt", {"max_tokens": 2}, {"user_id": userid})
            return lexicon['tokens_limit']
        return
