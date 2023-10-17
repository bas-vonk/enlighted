from sqlalchemy import BigInteger, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Production(Base):
    __tablename__ = "production"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_start: Mapped[int] = mapped_column(BigInteger)
    period_end: Mapped[int] = mapped_column(BigInteger)
    watt_hours: Mapped[float]
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="unique_period"),
    )
