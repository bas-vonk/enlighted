from time import time
from typing import Dict, List, Union

from sqlalchemy import BigInteger, String, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

unique_constraint_name_events = "unique_datapoint_events"
unique_constraint_name_values_timestamp = "unique_datapoint_values_timestamp"
unique_constraint_name_values_timestamp_hf = "unique_datapoint_values_timestamp_hf"
unique_constraint_name_values_time_window = "unique_datapoint_values_time_window"


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    device_brand: Mapped[str]
    device_name: Mapped[str] = mapped_column(String(16), index=True)
    observed_at: Mapped[int] = mapped_column(BigInteger, index=True)
    event: Mapped[str]
    reference: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint(
            "device_brand",
            "device_name",
            "observed_at",
            "event",
            name=unique_constraint_name_events,
        ),
    )

    @classmethod
    def upsert(
        cls, session: Session, rows: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        with session.get_bind(cls).connect() as conn:
            insert_statement = insert(cls).values(rows)
            upsert_statement = insert_statement.on_conflict_do_update(
                unique_constraint_name_events,
                set_=dict(
                    event=insert_statement.excluded.event,
                    reference=insert_statement.excluded.reference,
                ),
            )
            conn.execute(upsert_statement)
            conn.commit()


class ValueTimestamp(Base):
    __tablename__ = "values_timestamp"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    device_brand: Mapped[str]
    device_name: Mapped[str] = mapped_column(String(16), index=True)
    observation_name: Mapped[str] = mapped_column(String(32), index=True)
    observed_at: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[float]
    unit: Mapped[str]
    reference: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint(
            "device_brand",
            "device_name",
            "observation_name",
            "observed_at",
            name=unique_constraint_name_values_timestamp,
        ),
    )

    @classmethod
    def read(
        cls,
        session: Session,
        device_name,
        observation_name,
        observed_at_lower_bound=0,
        limit=None,
    ):
        with session.get_bind(cls).connect() as conn:
            select_statement = (
                select(cls.value, cls.observed_at)
                .where(cls.device_name == device_name)
                .where(cls.observation_name == observation_name)
                .where(cls.observed_at >= observed_at_lower_bound)
                .order_by(cls.observed_at.desc())
                .limit(limit)
            )
            resultproxy = conn.execute(select_statement)
            return [row._mapping for row in resultproxy.fetchall()]

    @classmethod
    def upsert(
        cls, session: Session, rows: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        with session.get_bind(cls).connect() as conn:
            insert_statement = insert(cls).values(rows)
            upsert_statement = insert_statement.on_conflict_do_update(
                unique_constraint_name_values_timestamp,
                set_=dict(
                    value=insert_statement.excluded.value,
                    unit=insert_statement.excluded.unit,
                    reference=insert_statement.excluded.reference,
                ),
            )
            conn.execute(upsert_statement)
            conn.commit()


class ValueTimestampHighFrequency(Base):
    __tablename__ = "values_timestamp_high_frequency"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    device_brand: Mapped[str]
    device_name: Mapped[str] = mapped_column(String(16), index=True)
    observation_name: Mapped[str]
    observed_at: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[float]
    unit: Mapped[str]
    reference: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint(
            "device_brand",
            "device_name",
            "observation_name",
            "observed_at",
            name=unique_constraint_name_values_timestamp_hf,
        ),
    )

    @classmethod
    def upsert(
        cls, session: Session, rows: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        with session.get_bind(cls).connect() as conn:
            insert_statement = insert(cls).values(rows)
            upsert_statement = insert_statement.on_conflict_do_update(
                unique_constraint_name_values_timestamp_hf,
                set_=dict(
                    value=insert_statement.excluded.value,
                    unit=insert_statement.excluded.unit,
                    reference=insert_statement.excluded.reference,
                ),
            )
            conn.execute(upsert_statement)
            conn.commit()


class ValueTimeWindow(Base):
    __tablename__ = "values_time_window"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(BigInteger, index=True, default=time)
    device_brand: Mapped[str]
    device_name: Mapped[str] = mapped_column(String(16), index=True)
    observation_name: Mapped[str]
    window_start: Mapped[int] = mapped_column(BigInteger, index=True)
    window_end: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[float]
    unit: Mapped[str]
    reference: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint(
            "device_brand",
            "device_name",
            "observation_name",
            "window_start",
            "window_end",
            name=unique_constraint_name_values_time_window,
        ),
    )

    @classmethod
    def upsert(
        cls, session: Session, rows: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        with session.get_bind(cls).connect() as conn:
            insert_statement = insert(cls).values(rows)
            upsert_statement = insert_statement.on_conflict_do_update(
                unique_constraint_name_values_time_window,
                set_=dict(
                    value=insert_statement.excluded.value,
                    unit=insert_statement.excluded.unit,
                    reference=insert_statement.excluded.reference,
                ),
            )
            conn.execute(upsert_statement)
            conn.commit()
