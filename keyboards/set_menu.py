from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    """Set list command menu button"""
    main_menu_commands = [
        BotCommand(command='/new',
                   description='Начать диалог заново(удалить сообщения)'),
        BotCommand(command='/new_dial',
                   description='Начать новый диалог'),
        BotCommand(command='/all_dial',
                   description='Выбрать диалог'),
        BotCommand(command='/weather',
                   description='Узнать погоду'),
        BotCommand(command='/cancel',
                   description='Отмена действия'),
        BotCommand(command='/show_balance',
                   description='Показать баланс'),
        BotCommand(command='/delete_all_dialogs',
                   description='Удалить все диалоги'),
        BotCommand(command='/pay',
                   description='Пополнить баланс'),
        BotCommand(command='/showdata',
                   description='Показать регистрационные данные'),
        BotCommand(command='/start',
                   description='Start bot'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/registration',
                   description='Регистрация'),

    ]
    await bot.set_my_commands(main_menu_commands)
