from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name = "unique_state"


class Base(DeclarativeBase):
    pass


class OperationState(Base):
    __tablename__ = "operation_states"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    haId: Mapped[str] = mapped_column(String(128), index=True)
    handling: Mapped[str]
    key: Mapped[str]
    level: Mapped[str]
    timestamp: Mapped[int] = mapped_column(BigInteger, index=True)
    uri: Mapped[str]
    value: Mapped[str]
    __table_args__ = (
        UniqueConstraint("haId", "timestamp", name=unique_constraint_name),
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
