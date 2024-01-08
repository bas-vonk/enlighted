from time import time
from typing import Dict, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name_indoor = "unique_measurement_indoor"
unique_constraint_name_outdoor = "unique_measurement_outdoor"


class Base(DeclarativeBase):
    pass


class IndoorMeasurement(Base):
    __tablename__ = "indoor_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    parameter_name: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[float]
    unit: Mapped[str]
    __table_args__ = (
        UniqueConstraint("parameter_name", "ts", name=unique_constraint_name_indoor),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, Union[str, float, int]]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(unique_constraint_name_indoor, set_=row)
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping


class OutdoorMeasurement(Base):
    __tablename__ = "outdoor_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    parameter_name: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[float]
    unit: Mapped[str]
    amount_of_stations: Mapped[int]
    __table_args__ = (
        UniqueConstraint("parameter_name", "ts", name=unique_constraint_name_outdoor),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, Union[str, float, int]]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(unique_constraint_name_outdoor, set_=row)
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping
