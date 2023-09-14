from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import Users, Wallet, Dialog, Transaction, Base
from sqlalchemy import TextClause, text, create_engine
from sqlalchemy import func, select, update, delete, Update, Select

from sqlalchemy.orm import Session
from sqlalchemy import ForeignKey, Row, RowMapping

from typing import List, Any, Sequence


class Crud:
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    async_session = Session(engine, expire_on_commit=False)
    Base.metadata.create_all(engine)

    @classmethod
    def insert(cls, *args) -> None:
        """
        Example: Crud.insert(Users(id=123, name="den", email="den@cher.com)),
                 Crud.insert(u1, u2, w1, t1, d1, .....))
        """
        with Session(cls.engine, expire_on_commit=False) as session:
            session.add_all([*args])
            session.commit()

    @classmethod
    def update(cls, obj, **where_param):
        """
        Example:
        Crud.update(Users(max_tokens=2), id=1)
        """
        table_param: dict = obj.get_args()
        where: TextClause = text(" AND ".join(
            [f"{obj.__tablename__}.{key} = '{val}'" for key, val in where_param.items()]))
        st: Update = obj.update().where(where)  # .values(**values)
        with Session(cls.engine, expire_on_commit=False) as session:
            session.execute(st, table_param)
            session.commit()

    @classmethod
    def select_cell(cls, cell, **where_param) -> Any:
        """
        Example: Crud.select_cell(Users.name, id=122, email="as@sad.we")
        """
        where: str = " AND ".join(f"{key} = :{key}" for key in where_param)
        stmt: Select = select(cell).where(text(where))
        with Session(cls.engine, expire_on_commit=False) as session:
            res = session.scalars(stmt, where_param)
            result = res.one()
            return result

    @classmethod
    def select_column(cls, instance) -> Sequence[Row | RowMapping | Any]:
        """
        example: Crud.select_column(Users.id)
        """
        if issubclass(instance.class_, Base):  # Проверить
            stmt: Select = select(instance)
            with Session(cls.engine, expire_on_commit=False) as session:
                res = session.scalars(stmt)
                result = res.all()
                return result
        else:
            raise ValueError

    @classmethod
    def select_columns(cls, *args) -> list[tuple]:
        """
        example: Crud.select_column(Users.id, Wallet.id, ....)
        """
        return [tuple(cls.select_column(el)) for el in args]

    @classmethod
    def select_row(cls, obj):
        """
        Example:
        Crud.select_row(Users(id=2))
        """
        table_param: dict = obj.get_args()
        where: TextClause = text(" AND ".join(
            [f"{obj.__tablename__}.{key} = '{val}'" for key, val in table_param.items()]
        ))
        st: Select = obj.select().where(where)
        with Session(cls.engine, expire_on_commit=False) as session:
            res = session.scalars(st).one()
            session.commit()
            return res

    @classmethod
    def delete(cls, obj):
        pass

    @classmethod
    def scalars(cls, stmt):
        with Session(cls.engine, expire_on_commit=False) as session:
            session.scalars(stmt)
            session.commit()

    @classmethod
    def data(cls, inst):
        # if issubclass(inst, Base):
        s = inst.get_args()
        print(type(inst), inst.__dict__['id'], inst.__repr__())
        print(inst.get_args())
        print(inst.__table__)
        print(s)
        t = text(" AND ".join([f":{key}" for key in s]))
        stmt = select(inst.return_self()).where(t)
        print(stmt)
        return stmt

    @classmethod
    def insert_update_user_registration_data(cls, userid: int, reg_data: dict) -> None:
        if userid not in cls.select_column(Users.id):
            reg_data.update()
            user = Users(**reg_data)
            wallet = Wallet(user=user)
            cls.insert(user, wallet)
        else:
            stmt = Users.update().where(Users.id == userid).values(**reg_data)
            cls.scalars(stmt)

        # with DateBase(DB_PATH) as db:
        #     if userid not in db.get_column(table=TABLE_NAME, name_column="user_id"):
        #         reg_data.update(tokens=100000)
        #         db.insert(table=TABLE_NAME, column_values=reg_data)
        #         db.insert(table=TABLE_NAME_FOR_MESSAGES, column_values={"user_id": userid,
        #                                                                 "messages": "[]",
        #                                                                 "tokens": 100000,
        #                                                                 "max_tokens": 0})
        #     else:
        #         db.update_values(table=TABLE_NAME, values=reg_data, params={"user_id": userid})


u1 = Users(id=122,
           name="den",
           email="as@sad.we")
u2 = Users(id=123, name="chery", email="sendy@mail.com")
w1 = Wallet(user=u1)

d1 = Dialog(name_chat="name chat",
            user=u1)

t1 = Transaction(sender=u1,
                 wallet="z242342342",
                 amount=0.5,
                 payment_no=1,
                 chat_id=2626262,
                 receiver_wallet=w1)


Crud.insert(u1, w1, d1, t1, u2)
