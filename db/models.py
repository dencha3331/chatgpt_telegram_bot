import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import func, select, update, delete, insert
from sqlalchemy import String, Float, JSON, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm.state import InstanceState


class Base(AsyncAttrs, DeclarativeBase):

    @classmethod
    def select(cls):
        """Create a select statement on this model."""
        return select(cls)

    @classmethod
    def update(cls):
        """Create an update statement on this model."""
        return update(cls)

    @classmethod
    def delete(cls):
        """Create a delete statement on this model."""
        return delete(cls)

    @classmethod
    def insert(cls):
        return insert(cls)

    @classmethod
    def return_self(cls):
        return cls

    def get_args(self):
        res = {}
        for key, val in self.__dict__.items():
            if not isinstance(val, InstanceState):
                res.update({key: val})
        return res


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_name: Mapped[str | None]
    user_name: Mapped[str | None] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str | None]
    age: Mapped[int | None]
    email: Mapped[str] = mapped_column(String(30), unique=True)
    gender: Mapped[str | None]
    wish_news: Mapped[bool | None]
    create_date: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now()
    )
    auth_email: Mapped[bool] = mapped_column(default=False)

    dialogs: Mapped[List["Dialog"] | None] = relationship(
        back_populates="user"
    )
    wallet: Mapped["Wallet"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_transactions: Mapped[List["Transaction"] | None] = relationship(
        back_populates="sender"
    )


class Dialog(Base):
    __tablename__ = "dialogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_chat: Mapped[str | None] = mapped_column(String(30))
    messages: Mapped[JSON] = mapped_column(JSON, default=[])
    model: Mapped[str | None] = mapped_column(String(30))
    images: Mapped[JSON] = mapped_column(JSON, default=[])
    max_tokens: Mapped[int] = mapped_column(Integer, default=0)
    current_dialog: Mapped[bool] = mapped_column(default=False)
    tokens_in_message: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="dialogs")

    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    wallet: Mapped["Wallet"] = relationship(back_populates="dialog")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[float] = mapped_column(Float(6), default=0.3)
    private_key: Mapped[str | None] = mapped_column(String(50), unique=True)
    address: Mapped[str | None] = mapped_column(String(50), unique=True)

    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="wallet")

    wallet_transactions: Mapped[List["Transaction"] | None] = relationship(
        back_populates="receiver_wallet")

    dialog: Mapped[List["Dialog"] | None] = relationship(
        back_populates="wallet"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    wallet: Mapped[str] = mapped_column(String(30))
    amount: Mapped[float] = mapped_column(Float(6))
    payment_no: Mapped[int] = mapped_column(unique=True)
    date_start_transaction: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now()
    )
    date_end_transaction: Mapped[datetime.datetime | None]
    tx_hash: Mapped[str | None] = mapped_column(String(50), unique=True)
    success: Mapped[bool] = mapped_column(default=False)
    fail: Mapped[bool] = mapped_column(default=False)
    result_message: Mapped[str | None] = mapped_column(String(50))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sender: Mapped["Users"] = relationship(
        back_populates="user_transactions"
    )
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    receiver_wallet: Mapped["Wallet"] = relationship(
        back_populates="wallet_transactions"
    )

