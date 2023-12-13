from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name = "unique_period"


class Base(DeclarativeBase):
    pass


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    readingTime: Mapped[int] = mapped_column(BigInteger)
    wNow: Mapped[int]
    activeCount: Mapped[int]
    __table_args__ = (UniqueConstraint("readingTime", name=unique_constraint_name),)

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, Union[str, float, int]]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(unique_constraint_name, set_=row)
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping
