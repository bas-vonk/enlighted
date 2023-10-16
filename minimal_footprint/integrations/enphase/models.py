from sqlalchemy import BigInteger, Column, Float, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Production(Base):
    __tablename__ = "production"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(BigInteger)
    period_end = Column(BigInteger)
    watt_hours = Column(Float)
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="unique_period"),
    )
