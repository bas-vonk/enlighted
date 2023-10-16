from sqlalchemy import BigInteger, Column, Integer, Text, select
from sqlalchemy.ext.declarative import declarative_base

from minimal_footprint.db import fetchone, insert_into
from minimal_footprint.utils import now

Base = declarative_base()


class AccessToken(Base):
    __tablename__ = "access_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(Text)
    expires_at = Column(BigInteger)

    @classmethod
    def store_token(cls, engine, token, expires_in, early_expire_factor=1.0):
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
    def get_most_recent(cls, db):
        """Get the most recent access token."""
        return fetchone(db, select(cls).order_by(cls.expires_at.desc()))


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    refresh_token = Column(Text)
    expires_at = Column(BigInteger)

    @classmethod
    def store_token(cls, engine, token, expires_in, early_expire_factor=1.0):
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
    def get_most_recent(cls, db):
        """Get the most recent access token."""
        return fetchone(db, select(cls).order_by(cls.expires_at.desc()))
