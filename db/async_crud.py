from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, Select, update, delete, TextClause, text, Row, RowMapping
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound

from aiogram.types import InlineKeyboardMarkup

from typing import Any, Sequence

from .models import Users, Wallet, Dialog, Transaction, Base
from keyboards import create_inline_callback_data_kb
from config_data import load_config
from lexicons import LEXICON_RU
from logs import logger

LEXICON: dict[str, str] = LEXICON_RU['user_handlers']


class Crud:
    db_data = load_config().db
    engine = create_async_engine(f"postgresql+asyncpg://{db_data.db_user}:{db_data.db_password}"
                                 f"@{db_data.db_host}/{db_data.database}", echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    @classmethod
    async def create_tables(cls):
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.drop_all)
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def insert(cls, *args) -> None:
        """
        Example: Crud.insert(Users(id=123, name="den", email="den@cher.com)),
                 Crud.insert(u1, u2, w1, t1, d1, .....))
        """
        async with cls.async_session() as session:
            async with session.begin():
                session.add_all([*args])
                await session.commit()

    # @classmethod
    # async def update(cls, obj, **where):
    #     """
    #     Example:
    #     Crud.update(Users(max_tokens=2, user_id=123), id=1)
    #     """
    #     table_param: dict = obj.get_args()
    #     where: TextClause = text(" AND ".join(
    #         [f"{obj.__tablename__}.{key} = '{val}'" for key, val in where.items()]))
    #     st: Update = obj.update().where(where)  # .values(**values)
    #     async with cls.async_session() as session:
    #         await session.execute(st, table_param)
    #         await session.commit()

    # @classmethod
    # async def update_many(cls, *obj, **where):
    #     """
    #     Example:
    #     Crud.update(Users(max_tokens=2, user_id=123), id=1)
    #     """
    #     table_param: dict = obj.get_args()
    #     where: TextClause = text(" AND ".join(
    #         [f"{obj.__tablename__}.{key} = '{val}'" for key, val in where.items()]))
    #     st: Update = obj.update().where(where)  # .values(**values)
    #     async with cls.async_session() as session:
    #         await session.execute(st, table_param)
    #         await session.commit()

    # @classmethod
    # async def select_cell(cls, cell, **where_param) -> Any:
    #     """
    #     Example: Crud.select_cell(Users.name, id=122, email="as@sad.we")
    #     """
    #     where: str = " AND ".join(f"{key} = :{key}" for key in where_param)
    #     stmt: Select = select(cell).where(text(where))
    #     async with cls.async_session() as session:
    #         res = await session.scalars(stmt, where_param)
    #         result = res.one()
    #         return result

    @classmethod
    # async def select_column(cls, instance) -> Sequence[Row | RowMapping | Any]:
    #     """
    #     example: Crud.select_column(Users.id)
    #     """
    #     if issubclass(instance.class_, Base):  # Проверить
    #         stmt: Select = select(instance)
    #         async with cls.async_session() as session:
    #             res = await session.scalars(stmt)
    #             result = res.all()
    #             return result
    #     else:
    #         raise ValueError

    # @classmethod
    # async def select_columns(cls, *args) -> list[tuple]:
    #     """
    #     example: Crud.select_column(Users.id, Wallet.id, ....)
    #     """
    #     return [tuple(await cls.select_column(el)) for el in args]

    # @classmethod
    # async def select_row(cls, obj):
    #     """
    #     Example:
    #     Crud.select_row(Users(id=2, ....))
    #     """
    #     table_param: dict = obj.get_args()
    #     where: TextClause = text(" AND ".join(
    #         [f"{obj.__tablename__}.{key} = '{val}'" for key, val in table_param.items()]
    #     ))
    #     st: Select = obj.select().where(where)
    #     async with cls.async_session() as session:
    #         res = await session.scalars(st)
    #         result = res.one()
    #         return result

    @classmethod
    def delete(cls, obj):
        pass

    @classmethod
    async def save_object(cls, obj):
        async with cls.async_session() as session:
            session.add(obj)
            await session.commit()

    @classmethod
    async def scalars(cls, stmt):
        async with cls.async_session() as session:
            res = await session.scalars(stmt)
            await session.commit()
            return res

    @classmethod
    async def get_user(cls, userid) -> Users | None:
        stmt = select(Users).where(Users.id == userid)
        async with cls.async_session() as session:
            res = await session.scalars(stmt)
            await session.commit()
            try:
                return res.one()
            except NoResultFound:
                return

    @classmethod
    async def get_dialogs(cls, userid) -> Sequence[Dialog]:
        stmt = select(Dialog).where(Dialog.user_id == userid)
        async with cls.async_session() as session:
            res = await session.scalars(stmt)
            await session.commit()
            return res.all()

    @classmethod
    async def get_wallet(cls, userid) -> Wallet:
        stmt = select(Wallet).where(Wallet.users_id == userid)
        async with cls.async_session() as session:
            res = await session.scalars(stmt)
            await session.commit()
            return res.one()

    @classmethod
    async def change_or_leave_model(cls, tg_id, model) -> None:
        stmt = update(Dialog).where(Dialog.user_id == tg_id) \
            .where(Dialog.current_dialog == True).values(model=model)
        async with cls.async_session() as session:
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_user_wallet_dialogs(cls, userid) -> Users | None:
        async with cls.async_session() as session:
            stmt = select(Users).options(selectinload(Users.wallet)
                                         ).options(selectinload(Users.dialogs)
                                                   ).where(Users.id == userid)
            result = await session.scalars(stmt)
            try:
                return result.one()
            except NoResultFound:
                return None

    @classmethod
    async def save_user_registration_data_in_db(cls, userid: int, reg_data: dict) -> None:
        user: Users | None = await cls.get_user(userid)

        if not user:
            user = Users(**reg_data)
            wallet = Wallet(user=user)
            await cls.insert(user, wallet)
        else:
            stmt = update(Users).where(Users.id == userid).values(**reg_data)
            async with cls.async_session() as session:
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def get_users_with_wallet(cls, userid: int) -> Users | None:
        stmt = select(Users).options(selectinload(Users.wallet)).where(Users.id == userid)
        async with cls.async_session() as session:
            result = await session.scalars(stmt)
            try:
                return result.one()
            except NoResultFound:
                return None

    @classmethod
    async def get_user_data_from_db(cls, userid: int) -> str:
        user: Users = await cls.get_users_with_wallet(userid)
        if not user:
            return LEXICON["empty_db"]
        return f'{LEXICON["show_db_name"]}: {user.name}\n' \
               f'{LEXICON["show_db_surname"]}: {user.surname}\n' \
               f'{LEXICON["show_db_age"]}: {user.age}\n' \
               f'{LEXICON["show_db_gender"]}: {LEXICON[user.gender]}\n' \
               f'{LEXICON["show_db_news"]}: {"Да" if user.wish_news else "нет"}\n' \
               f'{LEXICON["balance"]}: {user.wallet.balance}'

    @classmethod
    async def get_users_with_dialog(cls, userid: int) -> Users | None:
        stmt = select(Users).options(selectinload(Users.dialogs)).where(Users.id == userid)
        async with cls.async_session() as session:
            result = await session.scalars(stmt)
            try:
                return result.one()
            except NoResultFound:
                return None

    @classmethod
    async def clear_dialog(cls, userid: int) -> str:
        user: Users = await cls.get_users_with_dialog(userid)
        if not user:
            return "Пройдите регистрацию"
        try:
            current_dialog: Dialog = [dialog for dialog in user.dialogs if dialog.current_dialog][0]
            current_dialog.messages = []
            logger.info(f"Удалены сообщения с {userid} dialog_id: {current_dialog.id}")
        except IndexError:
            dialog: Dialog = Dialog(user=user, current_dialog=True)
            user.dialogs.append(dialog)
            logger.info(f"Не найден текущий диалог создаю новый {userid}")
        await cls.save_object(user)
        return f"{LEXICON['/new']}"

    @classmethod
    async def new_dialog(cls, userid: int) -> str:
        user: Users = await cls.get_user_wallet_dialogs(userid)
        wallet_id = user.wallet.id
        if not user:
            return "Пройдите регистрацию"
        dialogs: list[Dialog] = user.dialogs
        if len(dialogs) < 10:
            for dialog in dialogs:
                dialog.current_dialog = False
        else:
            return "Всего можно использовать 10 диалогов удалите ненужные и повторите"
        dialog: Dialog = Dialog(user=user, current_dialog=True, wallet_id=wallet_id)
        user.dialogs.append(dialog)
        await cls.save_object(user)
        logger.info(f"Начат новый диалог с {userid}")
        return f"{LEXICON['/new_dial']}"

    @classmethod
    async def choice_dial(cls, userid: int) -> InlineKeyboardMarkup:
        user: Users = await cls.get_users_with_dialog(userid)
        dialogs: list[Dialog] = user.dialogs
        buttons = {}
        for dialog in dialogs:
            if not dialog.current_dialog:
                buttons[str(dialog.id)] = dialog.name_chat
            else:
                buttons[str(dialog.id)] = dialog.name_chat + "   (*активный)"
        keyboard: InlineKeyboardMarkup = create_inline_callback_data_kb(
            1, last_btn={"no_choice": "Не выбирать"}, **buttons
        )
        return keyboard

    @classmethod
    async def change_current_dialog(cls, userid, dialog_id) -> str | bool:
        user: Users = await cls.get_users_with_dialog(userid)
        dialogs: list[Dialog] = user.dialogs
        if dialog_id not in [dialog.id for dialog in dialogs]:
            return False
        result: str = ""
        for dialog in dialogs:
            dialog.current_dialog = False
            if dialog.id == dialog_id:
                dialog.current_dialog = True
                result = dialog.name_chat
        await cls.save_object(user)
        return result

    @classmethod
    async def show_balance(cls, userid: int) -> str:
        try:
            wallet: Wallet = await cls.get_wallet(userid)
            return str(wallet.balance)
        except NoResultFound:
            return "Пройдите регистрацию"

    @classmethod
    async def clear_all_active_dialog(cls, userid: int) -> None:
        user: Users = await cls.get_users_with_dialog(userid)
        if not user:
            return
        dialogs: list[Dialog] = user.dialogs
        for dialog in dialogs:
            dialog.current_dialog = False
        await cls.save_object(user)

    @classmethod
    async def delete_all_dialogs(cls, userid):
        stmt = delete(Dialog).where(Dialog.user_id == userid)
        async with cls.async_session() as session:
            await session.execute(stmt)
            await session.commit()


async def main() -> None:
    u1 = Users(id=122,
               name="den",
               email="as@sad.we")
    u2 = Users(id=123, name="chery", email="sendy@mail.com")
    w1 = Wallet(user=u1)

    d1 = Dialog(name_chat="name chat",
                user=u1,
                messages=[{'role': 'user', 'content': "Кто ты воин"}],
                max_tokens=1,
                wallet=w1)

    d2 = Dialog(name_chat="name chat2",
                user=u1,
                messages=[{'role': 'user', 'content': "Кто ты воин"}],
                max_tokens=1,
                wallet=w1,
                current_dialog=True)

    t1 = Transaction(sender=u1,
                     wallet="z242342342",
                     amount=0.5,
                     payment_no=1,
                     chat_id=2626262,
                     receiver_wallet=w1)

    db_data = load_config().db
    engine = create_async_engine(f"postgresql+asyncpg://{db_data.db_user}:{db_data.db_password}"
                                 f"@{db_data.db_host}/{db_data.database}", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await Crud.insert(u1, w1, d1, d2, t1, u2)
    await engine.dispose()
    await Crud.delete_all_dialogs(122)
    res = await Crud.get_user_wallet_dialogs(111)
    print(res)

    # res = await Crud.select_column(Users.id)
#     print(res)
#     # dial = await Crud.select_cell(Dialog.messages, user_id=122)
#     # print(type(dial), dial)
#     if await Crud.select_cell(Dialog.max_tokens, id=1):
#         print("OK")
#     # await Crud.get_user_data_from_db(122)
#     # stmt = select(Users).options(selectinload(Users.wallet)).where(Users.id == 122)
#     # rese = await Crud.scalars(stmt)
#     # print(rese.one().wallet.users_id)
#     chat_messages = [{'role': 'user', 'content': "who are you, warrior"},
#                      {'role': 'assist', 'content': "Akhilesh"}]
#     user = await Crud.get_user_wallet_dialogs(122)
#     user1 = await Crud.get_user_wallet_dialogs(12222222)
#     print(user1, "oouuuueeeee")
#     dialogs: list[Dialog] = user.dialogs
#     dialog: Dialog = [dial for dial in dialogs if dial.current_dialog][-1]
#     wallet: Wallet = user.wallet
#     current_balance: float = wallet.balance
#     pay: float = 0.02
#     final_balance = current_balance - pay
#     wallet.balance = final_balance
#     if dialog.name_chat:
#         dialog.name_chat = chat_messages[-2]['content'][:15]
#     await Crud.save_object(user)
#     # wallet.balance = 12.333
#     # async_session = async_sessionmaker(engine, expire_on_commit=False)
#     # async with async_session() as session:
#     #     session.add(user)
#     #     await session.commit()
#     # await session.flush()
#     # stm = select(user)
#     # print(stm)
#     # await test_asd(122)
#     ser: Wallet = await Crud.get_wallet_row(122)
#     print(ser.balance)
#     await Crud.change_or_leave_model(122, "model32")
#     wa = await Crud.get_user_row(12121)
#     print(wa)
#     # func()
#     # print(user.wallet.id)
#     # dfg = tuple(filter(lambda x: x.current_dialog, user.dialogs))[0]
#     # print([us.name_chat for us in user.dialogs if us.current_dialog][-1])
#
#     # print(dfg.name_chat)
#     # for el in user.dialogs:
#     #     print(el.id)
#     # for el in sed:
#     #     print(el)


# async def test_asd(er):
#     user: Users = await Crud.get_user_wallet_dialogs(er)
#     dialog: Dialog = [dialog for dialog in user.dialogs if dialog.current_dialog][-1]
#     dialog.model = "gpt34444444"
#     await test2(user)
#
#
# async def test2(obj):
#     await Crud.save_object(obj)


# asyncio.run(main())
