from sqlalchemy import BigInteger, Integer, Text, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from minimal_footprint.db import fetchone, insert_into
from minimal_footprint.utils import now


class Base(DeclarativeBase):
    pass


class AccessToken(Base):
    __tablename__ = "access_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    access_token: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[int] = mapped_column(BigInteger)

    @classmethod
    def store_token(
        cls,
        engine: Engine,
        token: str,
        expires_in: int,
        early_expire_factor: float = 1.0,
    ) -> None:
        """Store the access token"""
        insert_into(
            cls,
            engine,
            {
                "access_token": token,
                "expires_at": now() + expires_in * early_expire_factor,
            },
        )

    @classmethod
    def get_most_recent(cls, engine: Engine) -> dict:
        """Get the most recent access token."""
        return fetchone(engine, select(cls).order_by(cls.expires_at.desc()))


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refresh_token: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[int] = mapped_column(BigInteger)

    @classmethod
    def store_token(
        cls,
        engine: Engine,
        token: str,
        expires_in: int,
        early_expire_factor: float = 1.0,
    ) -> None:
        """Store the refresh token."""
        insert_into(
            cls,
            engine,
            {
                "refresh_token": token,
                "expires_at": now() + expires_in * early_expire_factor,
            },
        )

    @classmethod
    def get_most_recent(cls, engine: Engine) -> dict:
        """Get the most recent access token."""
        return fetchone(engine, select(cls).order_by(cls.expires_at.desc()))
