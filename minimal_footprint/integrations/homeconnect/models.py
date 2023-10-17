from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class OperationState(Base):
    __tablename__ = "operation_states"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appliance_name: Mapped[str] = mapped_column(String(128))
    datetime_stored: Mapped[int] = mapped_column(BigInteger)
    state: Mapped[str] = mapped_column(String(128))
    __table_args__ = (
        UniqueConstraint("appliance_name", "datetime_stored", name="unique_state"),
    )
