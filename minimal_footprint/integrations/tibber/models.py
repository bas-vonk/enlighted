from sqlalchemy import BigInteger, Column, Float, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Consumption(Base):
    __tablename__ = "consumption"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(BigInteger, index=True)
    period_end = Column(BigInteger, index=True)
    unit_price = Column(Float)
    cost = Column(Float)
    consumption = Column(Float)
    consumption_unit = Column(String(8))
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="consumption_unique_entry"),
    )


class Production(Base):
    __tablename__ = "production"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(BigInteger, index=True)
    period_end = Column(BigInteger, index=True)
    unit_price = Column(Float)
    revenue = Column(Float)
    production = Column(Float)
    production_unit = Column(String(8))
    __table_args__ = (
        UniqueConstraint("period_start", "period_end", name="production_unique_entry"),
    )
