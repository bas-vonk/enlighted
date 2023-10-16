from sqlalchemy import BigInteger, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OperationState(Base):
    __tablename__ = "operation_states"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appliance_name = Column(String(128))
    datetime_stored = Column(BigInteger)
    state = Column(String(128))
    __table_args__ = (
        UniqueConstraint("appliance_name", "datetime_stored", name="unique_state"),
    )
