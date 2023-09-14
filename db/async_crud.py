from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from models import Users, Wallet, Dialog, Transaction, Base
from sqlalchemy import TextClause, text
from sqlalchemy import select, Update, Select, update, delete
from sqlalchemy import Row, RowMapping

from typing import Any, Sequence
import asyncio

from config_data import load_config
from lexicons import LEXICON_RU
from logs import logger


LEXICON: dict[str, str] = LEXICON_RU['user_handlers']


class Crud:
    db_data = load_config().db
    engine = create_async_engine(f"postgresql+asyncpg://{db_data.db_user}:{db_data.db_password}"
                                 f"@{db_data.db_host}/{db_data.database}", echo=True)
    # Base.metadata.create_all(engine)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

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

    @classmethod
    async def update(cls, obj, **where):
        """
        Example:
        Crud.update(Users(max_tokens=2, user_id=123), id=1)
        """
        table_param: dict = obj.get_args()
        where: TextClause = text(" AND ".join(
            [f"{obj.__tablename__}.{key} = '{val}'" for key, val in where.items()]))
        st: Update = obj.update().where(where)  # .values(**values)
        async with cls.async_session() as session:
            await session.execute(st, table_param)
            await session.commit()
            
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

    @classmethod
    async def select_cell(cls, cell, **where_param) -> Any:
        """
        Example: Crud.select_cell(Users.name, id=122, email="as@sad.we")
        """
        where: str = " AND ".join(f"{key} = :{key}" for key in where_param)
        stmt: Select = select(cell).where(text(where))
        async with cls.async_session() as session:
            res = await session.scalars(stmt, where_param)
            result = res.one()
            return result

    @classmethod
    async def select_column(cls, instance) -> Sequence[Row | RowMapping | Any]:
        """
        example: Crud.select_column(Users.id)
        """
        if issubclass(instance.class_, Base):  # Проверить
            stmt: Select = select(instance)
            async with cls.async_session() as session:
                res = await session.scalars(stmt)
                result = res.all()
                return result
        else:
            raise ValueError

    @classmethod
    async def select_columns(cls, *args) -> list[tuple]:
        """
        example: Crud.select_column(Users.id, Wallet.id, ....)
        """
        return [tuple(await cls.select_column(el)) for el in args]

    @classmethod
    async def select_row(cls, obj):
        """
        Example:
        Crud.select_row(Users(id=2, ....))
        """
        table_param: dict = obj.get_args()
        where: TextClause = text(" AND ".join(
            [f"{obj.__tablename__}.{key} = '{val}'" for key, val in table_param.items()]
        ))
        st: Select = obj.select().where(where)
        async with cls.async_session() as session:
            res = await session.scalars(st)
            result = res.one()
            return result

    @classmethod
    def delete(cls, obj):
        pass

    @classmethod
    async def scalars(cls, stmt):
        async with cls.async_session() as session:
            await session.scalars(stmt)
            await session.commit()

    @classmethod
    async def save_user_registration_data_in_db(cls, userid: int, reg_data: dict) -> None:
        if userid not in await cls.select_column(Users.id):
            user = Users(**reg_data)
            wallet = Wallet(user=user)
            await cls.insert(user, wallet)
        else:
            await cls.update(Users(**reg_data), id=userid)

    @classmethod
    async def get_user_data_from_db(cls, userid: int) -> str:
        users_id: Sequence = await cls.select_column(Users.id)
        if userid not in users_id:
            return LEXICON["empty_db"]
        row: Users = await cls.select_row(Users(id=userid))
        return f'{LEXICON["show_db_name"]}: {row.user_name}\n' \
               f'{LEXICON["show_db_surname"]}: {row.surname}\n' \
               f'{LEXICON["show_db_age"]}: {row.age}\n' \
               f'{LEXICON["show_db_gender"]}: {LEXICON[row.gender]}\n' \
               f'{LEXICON["show_db_news"]}: {"Да" if row.wish_news else "нет"}\n'

    @classmethod
    async def new_dialog(cls, userid: int) -> str:
        if userid not in await cls.select_column(Users.id):
            return "Пройдите регистрацию"
        user: Users = await Crud.select_row(Users(id=userid))
        dialog: Dialog = Dialog(user=user, current_dialog=True)
        await Crud.insert(dialog)
        logger.info(f"Начат новый диалог с {userid}")
        return f"{LEXICON['/new']}"


async def main() -> None:
    u1 = Users(id=122,
               name="den",
               email="as@sad.we")
    u2 = Users(id=123, name="chery", email="sendy@mail.com")
    w1 = Wallet(user=u1)

    d1 = Dialog(name_chat="name chat",
                user=u1, messages=[{'role': 'user', 'content': "Кто ты воин"}],
                max_tokens=1)

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
    await Crud.insert(u1, w1, d1, t1, u2)
    await engine.dispose()
    res = await Crud.select_column(Users.id)
    print(res)
    dial = await Crud.select_cell(Dialog.messages, user_id=122)
    print(type(dial), dial)
    if await Crud.select_cell(Dialog.max_tokens, id=1):
        print("OK")
    await Crud.get_user_data_from_db(122)


asyncio.run(main())
