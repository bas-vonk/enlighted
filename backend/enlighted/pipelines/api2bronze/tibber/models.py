from time import time
from typing import Dict, Optional, Union

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

live_ticker_unique_constraint_name = "live_ticker_unique_entry"
consumption_unique_constraint_name = "consumption_unique_entry"
production_unique_constraint_name = "production_unique_entry"


class Base(DeclarativeBase):
    pass


class LiveTicker(Base):
    __tablename__ = "live_ticker"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    accumulatedConsumption: Mapped[float]
    accumulatedConsumptionLastHour: Mapped[float]
    accumulatedCost: Mapped[float]
    accumulatedProduction: Mapped[float]
    accumulatedProductionLastHour: Mapped[float]
    accumulatedReward: Mapped[float]
    averagePower: Mapped[float]
    currency: Mapped[str]
    currentL1: Mapped[int]
    currentL2: Mapped[int]
    currentL3: Mapped[int]
    estimatedHourConsumption: Mapped[float]
    lastMeterConsumption: Mapped[float]
    lastMeterProduction: Mapped[float]
    maxPower: Mapped[int]
    minPower: Mapped[int]
    power: Mapped[int]
    powerFactor: Mapped[float | None]
    powerProduction: Mapped[float]
    powerReactive: Mapped[float | None]
    signalStrength: Mapped[int | None]
    timestamp: Mapped[int] = mapped_column(BigInteger, index=True)
    voltagePhase1: Mapped[float]
    voltagePhase2: Mapped[float]
    voltagePhase3: Mapped[float]
    __table_args__ = (
        UniqueConstraint("timestamp", name=live_ticker_unique_constraint_name),
    )

    @classmethod
    def upsert(cls, session: Session, row: Dict[str, int]) -> None:
        with session.get_bind(cls).connect() as conn:
            res = conn.execute(
                insert(cls)
                .values(row)
                .on_conflict_do_update(live_ticker_unique_constraint_name, set_=row)
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
    cost: Mapped[Optional[float]]
    unitPrice: Mapped[float]
    unitPriceVAT: Mapped[float]
    consumption: Mapped[Optional[float]]
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
    profit: Mapped[Optional[float]]
    unitPrice: Mapped[float]
    unitPriceVAT: Mapped[float]
    production: Mapped[Optional[float]]
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
