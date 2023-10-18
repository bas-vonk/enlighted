from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

unique_constraint_name = "unique_period"


class Base(DeclarativeBase):
    pass


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger)
    period_end: Mapped[int] = mapped_column(BigInteger)
    watt_hours: Mapped[float]
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name=unique_constraint_name),
    )

    @classmethod
    def upsert(cls, engine: Engine, row: Dict[str, Union[str, float, int]]) -> None:
        with engine.connect() as conn:
            conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(unique_constraint_name, set_=row)
            )
            conn.commit()
