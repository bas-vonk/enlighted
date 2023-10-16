from sqlalchemy import BigInteger, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Consumption(Base):
    __tablename__ = "consumption"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger, index=True)
    period_end: Mapped[int] = mapped_column(BigInteger, index=True)
    unit_price: Mapped[float]
    cost: Mapped[float]
    consumption: Mapped[float]
    consumption_unit: Mapped[str]
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="consumption_unique_entry"),
    )


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger, index=True)
    period_end: Mapped[int] = mapped_column(BigInteger, index=True)
    unit_price: Mapped[float]
    revenue: Mapped[float]
    production: Mapped[float]
    production_unit: Mapped[str]
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="production_unique_entry"),
    )
