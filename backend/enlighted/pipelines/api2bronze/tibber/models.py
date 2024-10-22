from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

consumption_unique_constraint_name = "consumption_unique_entry"
production_unique_constraint_name = "production_unique_entry"


class Base(DeclarativeBase):
    pass


class Consumption(Base):
    __tablename__ = "consumption"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    From: Mapped[int] = mapped_column(BigInteger, index=True)
    To: Mapped[int] = mapped_column(BigInteger, index=True)
    cost: Mapped[float | None]
    unitPrice: Mapped[float | None]
    unitPriceVAT: Mapped[float | None]
    consumption: Mapped[float | None]
    consumptionUnit: Mapped[str] = mapped_column(String(16))
    __table_args__ = (
        UniqueConstraint("From", "To", name=consumption_unique_constraint_name),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, Union[str, float, int]]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(consumption_unique_constraint_name, set_=row)
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    From: Mapped[int] = mapped_column(BigInteger, index=True)
    To: Mapped[int] = mapped_column(BigInteger, index=True)
    profit: Mapped[float | None]
    unitPrice: Mapped[float | None]
    unitPriceVAT: Mapped[float | None]
    production: Mapped[float | None]
    productionUnit: Mapped[str] = mapped_column(String(16))
    __table_args__ = (
        UniqueConstraint("From", "To", name=production_unique_constraint_name),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, Union[str, float, int]]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(production_unique_constraint_name, set_=row)
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping
