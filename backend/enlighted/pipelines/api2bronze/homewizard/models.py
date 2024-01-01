from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name = "unique_measurement"


class Base(DeclarativeBase):
    pass


class Measurement(Base):
    __tablename__ = "measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    observation_name: Mapped[str] = mapped_column(String(64), index=True)
    total_power_import_t1_kwh: Mapped[float]
    total_power_export_t1_kwh: Mapped[float]
    active_power_w: Mapped[float]
    active_power_l1_w: Mapped[float]
    __table_args__ = (
        UniqueConstraint("created", "observation_name", name=unique_constraint_name),
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
