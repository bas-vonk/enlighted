from sqlalchemy import BigInteger, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    parameter_id = Column(Integer)
    parameter_name = Column(String(64))
    datetime_stored = Column(BigInteger)
    display_value = Column(String(16))
    unit = Column(String(8))
    designation = Column(String(128))
    __table_args__ = (
        UniqueConstraint("datetime_stored", "parameter_id", name="unique_observation"),
    )
