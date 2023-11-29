from typing import Optional

from sqlalchemy import BigInteger, Integer, Text, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import TypedDict

from minimal_footprint.utils import now

AccessTokenRow = TypedDict("AccessTokenRow", {"access_token": str, "expires_at": int})
RefreshTokenRow = TypedDict(
    "RefreshTokenRow", {"refresh_token": str, "expires_at": int}
)


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
        with engine.connect() as conn:
            conn.execute(
                insert(cls).values(
                    {
                        "access_token": token,
                        "expires_at": now() + expires_in * early_expire_factor,
                    }
                )
            )
            conn.commit()

    @classmethod
    def get_most_recent(cls, engine: Engine) -> Optional[AccessTokenRow]:
        """Get the most recent access token."""
        with engine.connect() as conn:
            exec = conn.execute(select(cls).order_by(cls.expires_at.desc()))
            row = exec.fetchone()

            if row is None:
                return None

            return {
                "access_token": row._mapping.access_token,
                "expires_at": row._mapping.expires_at,
            }


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
        with engine.connect() as conn:
            conn.execute(
                insert(cls).values(
                    {
                        "refresh_token": token,
                        "expires_at": now() + expires_in * early_expire_factor,
                    }
                )
            )
            conn.commit()

    @classmethod
    def get_most_recent(cls, engine: Engine) -> Optional[RefreshTokenRow]:
        """Get the most recent refresh token."""
        with engine.connect() as conn:
            exec = conn.execute(select(cls).order_by(cls.expires_at.desc()))
            row = exec.fetchone()

            if row is None:
                return None

            return {
                "refresh_token": row._mapping.refresh_token,
                "expires_at": row._mapping.expires_at,
            }
