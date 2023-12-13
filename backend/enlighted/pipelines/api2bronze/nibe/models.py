from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name = "unique_observation"


class Base(DeclarativeBase):
    pass


class Data(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    parameterId: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(128), index=True)
    displayValue: Mapped[str] = mapped_column(String(16))
    unit: Mapped[str] = mapped_column(String(8))
    designation: Mapped[str] = mapped_column(String(128))
    __table_args__ = (
        UniqueConstraint("created", "parameterId", name=unique_constraint_name),
    )

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
