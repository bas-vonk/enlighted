from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

consumption_unique_constraint_name = "consumption_unique_entry"
production_unique_constraint_name = "production_unique_entry"


class Base(DeclarativeBase):
    pass


class Consumption(Base):
    __tablename__ = "consumption"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger, index=True)
    period_end: Mapped[int] = mapped_column(BigInteger, index=True)
    unit_price: Mapped[float]
    cost: Mapped[float]
    consumption: Mapped[float]
    consumption_unit: Mapped[str] = mapped_column(String(16))
    __table_args__ = (
        UniqueConstraint(
            "period_start", "period_end", name=consumption_unique_constraint_name
        ),
    )

    @classmethod
    def upsert(cls, engine: Engine, row: Dict[str, Union[str, float, int]]) -> None:
        with engine.connect() as conn:
            conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(consumption_unique_constraint_name, set_=row)
            )
            conn.commit()


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger, index=True)
    period_end: Mapped[int] = mapped_column(BigInteger, index=True)
    unit_price: Mapped[float]
    revenue: Mapped[float]
    production: Mapped[float]
    production_unit: Mapped[str] = mapped_column(String(16))
    __table_args__ = (
        UniqueConstraint(
            "period_start", "period_end", name=production_unique_constraint_name
        ),
    )

    @classmethod
    def upsert(cls, engine: Engine, row: Dict[str, Union[str, float, int]]) -> None:
        with engine.connect() as conn:
            conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(production_unique_constraint_name, set_=row)
            )
            conn.commit()
