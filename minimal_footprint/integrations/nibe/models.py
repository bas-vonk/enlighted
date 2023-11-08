from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

unique_constraint_name = "unique_observation"


class Base(DeclarativeBase):
    pass


class Data(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parameter_id: Mapped[int] = mapped_column(Integer, index=True)
    parameter_name: Mapped[str] = mapped_column(String(64), index=True)
    datetime_stored: Mapped[int] = mapped_column(BigInteger, index=True)
    display_value: Mapped[str] = mapped_column(String(16))
    unit: Mapped[str] = mapped_column(String(8))
    designation: Mapped[str] = mapped_column(String(128))
    __table_args__ = (
        UniqueConstraint(
            "datetime_stored", "parameter_id", name=unique_constraint_name
        ),
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
