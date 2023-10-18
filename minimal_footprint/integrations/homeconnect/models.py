from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

unique_constraint_name = "unique_state"


class Base(DeclarativeBase):
    pass


class OperationState(Base):
    __tablename__ = "operation_states"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appliance_name: Mapped[str] = mapped_column(String(128))
    datetime_stored: Mapped[int] = mapped_column(BigInteger)
    state: Mapped[str] = mapped_column(String(128))
    __table_args__ = (
        UniqueConstraint(
            "appliance_name", "datetime_stored", name=unique_constraint_name
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
