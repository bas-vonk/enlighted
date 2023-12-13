from typing import Dict, List, Union

from sqlalchemy import BigInteger, Integer, MetaData, UniqueConstraint, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

unique_constraint_name = "unique_datapoint"


class Base(DeclarativeBase):
    metadata = MetaData(schema="silver")


class Data(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_brand: Mapped[str]
    device_name: Mapped[str]
    observation_name: Mapped[str]
    observed_at: Mapped[int] = mapped_column(BigInteger)
    value: Mapped[float]
    unit: Mapped[str]
    reference: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint(
            "device_brand",
            "device_name",
            "observation_name",
            "observed_at",
            name=unique_constraint_name,
        ),
    )

    @classmethod
    def upsert(
        cls, engine: Engine, rows: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        with engine.connect() as conn:
            insert_statement = insert(cls).values(rows)
            upsert_statement = insert_statement.on_conflict_do_update(
                unique_constraint_name,
                set_=dict(
                    value=insert_statement.excluded.value,
                    unit=insert_statement.excluded.unit,
                    reference=insert_statement.excluded.reference,
                ),
            )
            conn.execute(upsert_statement)
            conn.commit()
