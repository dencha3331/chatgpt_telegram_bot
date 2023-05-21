from __future__ import annotations

from aiogram import Bot
from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    # admin_ids: list[int]  # Список id администраторов бота


@dataclass
class OpenAI:
    token: str  # Токен для доступа к OpenAI


@dataclass
class Config:
    tg_bot: TgBot
    open_ai: OpenAI
    # db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        open_ai=OpenAI(env('OPENAI_API_KEY')),
    )


configs: Config = load_config()
bot: Bot = Bot(token=configs.tg_bot.token,
               parse_mode="HTML")
