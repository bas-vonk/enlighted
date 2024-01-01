from time import time
from typing import Dict, Optional, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

live_measurements_unique_constraint_name = "live_measurements_unique_entry"
consumption_unique_constraint_name = "consumption_unique_entry"
production_unique_constraint_name = "production_unique_entry"


class Base(DeclarativeBase):
    pass


class LiveMeasurement(Base):
    __tablename__ = "live_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)

    accumulatedCost: Mapped[float]
    accumulatedReward: Mapped[float]
    accumulatedProduction: Mapped[float]
    accumulatedConsumption: Mapped[float]
    accumulatedProductionLastHour: Mapped[float]
    accumulatedConsumptionLastHour: Mapped[float]
    averagePower: Mapped[float]
    currency: Mapped[str]
    currentL1: Mapped[int]
    currentL2: Mapped[int]
    currentL3: Mapped[int]
    lastMeterConsumption: Mapped[float]
    lastMeterProduction: Mapped[float]
    maxPower: Mapped[int]
    maxPowerProduction: Mapped[float]
    minPower: Mapped[int]
    minPowerProduction: Mapped[float]
    power: Mapped[int]
    powerFactor: Mapped[float | None]
    powerProduction: Mapped[float]
    powerProductionReactive: Mapped[float | None]
    powerReactive: Mapped[float | None]
    signalStrength: Mapped[int | None]
    timestamp: Mapped[int] = mapped_column(BigInteger, index=True)
    voltagePhase1: Mapped[float]
    voltagePhase2: Mapped[float]
    voltagePhase3: Mapped[float]
    __table_args__ = (
        UniqueConstraint("timestamp", name=live_measurements_unique_constraint_name),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, int]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(
                    live_measurements_unique_constraint_name, set_=row
                )
                .returning(cls)
            )
            conn.commit()
            return res.fetchone()._mapping


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
