from time import time
from typing import Any, Dict, Union

from sqlalchemy import BigInteger, String, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import JSON, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name = "unique_insights"


class Base(DeclarativeBase):
    type_annotation_map = {Dict[str, Any]: JSON}


class DailyPowerUsage(Base):
    __tablename__ = "daily_power_usage"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    day_start_timestamp: Mapped[int] = mapped_column(BigInteger, index=True)
    device_name: Mapped[str] = mapped_column(String(16), index=True)
    daily_power_used_total_watt_hours: Mapped[float]
    daily_power_used_in_rest_watt_hours: Mapped[float]
    daily_power_used_active_watt_hours: Mapped[float]
    moving_average_daily_power_used_total_watt_hours: Mapped[float]
    moving_average_daily_power_used_in_rest_watt_hours: Mapped[float]
    moving_average_daily_power_used_active_watt_hours: Mapped[float]
    current_power_consumption_watts: Mapped[float]


class Insight(Base):
    __tablename__ = "insights"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    insight_name: Mapped[str]
    insight: Mapped[Dict[str, Any]]
    observed_at: Mapped[int] = mapped_column(BigInteger, index=True)
    __table_args__ = (
        UniqueConstraint(
            "insight_name",
            "created_at",
            "observed_at",
            name=unique_constraint_name,
        ),
    )

    @classmethod
    def read(cls, session: Session, insight_name: str):
        with session.get_bind(cls).connect() as conn:
            select_statement = (
                select(cls)
                .where(cls.insight_name == insight_name)
                .order_by(cls.observed_at.desc())
                .order_by(cls.created_at.desc())
                .limit(1)
            )
            resultproxy = conn.execute(select_statement)
            return resultproxy.fetchone()._mapping

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
