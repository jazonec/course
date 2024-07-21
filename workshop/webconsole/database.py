import os

from sqlalchemy import DateTime, Boolean, String, Numeric, ForeignKey, select, update, create_engine, BIGINT, func, sql
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import Mapped, mapped_column, relationship

pg_host = os.getenv("DB_HOST")
pg_port = int(os.getenv("DB_PORT"))
pg_user = os.getenv("POSTGRES_USER")
pg_pass = os.getenv("POSTGRES_PASSWORD")
pg_base = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_base}", echo=True)

class Base(DeclarativeBase):
  pass

def get_engine():
    return Session(engine)

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[BIGINT] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str] = mapped_column(String(120))
    email: Mapped[str]
    created = mapped_column(DateTime, nullable=False, server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default=sql.false())
    allow_prompt: Mapped[bool] = mapped_column(Boolean, server_default=sql.false())
    allow_dalle: Mapped[bool] = mapped_column(Boolean, server_default=sql.false())

    user_balance: Mapped["UserBalance"] = relationship(back_populates="user")

class UserBalance(Base):
    __tablename__ = "user_balance"

    user_id = mapped_column(BIGINT, ForeignKey("users.user_id"), primary_key=True)
    balance = mapped_column(Numeric(15,2))
    
    user: Mapped["User"] = relationship(back_populates="user_balance")

# class UserBalanceDetail(Base):
#    __tablename__ = "user_balance_detail"
#
#    id: Mapped[int] = mapped_column(Integer, primary_key=True)
#    user_id = mapped_column(BIGINT, ForeignKey("user.id"))
#    operation_date = mapped_column(DateTime, nullable=False)
#    incoming = mapped_column(Numeric)
#    outcoming = mapped_column(Numeric)

#Base.metadata.create_all(engine)