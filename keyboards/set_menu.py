from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    """Set list command menu button"""
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Start bot'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/new',
                   description='Начать диалог с начала'),
        BotCommand(command='/weather',
                   description='Узнать погоду'),
        BotCommand(command='/registration',
                   description='Регистрация'),
        BotCommand(command='/cancel',
                   description='Отмена действия'),
        BotCommand(command='/showdata',
                   description='Показать регистрационные данные'),
    ]
    await bot.set_my_commands(main_menu_commands)
