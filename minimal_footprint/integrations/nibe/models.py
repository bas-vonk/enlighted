from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Data(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parameter_id: Mapped[int]
    parameter_name: Mapped[str] = mapped_column(String(64))
    datetime_stored: Mapped[int] = mapped_column(BigInteger)
    display_value: Mapped[str] = mapped_column(String(16))
    unit: Mapped[str] = mapped_column(String(8))
    designation: Mapped[str] = mapped_column(String(128))
    __table_args__ = (
        UniqueConstraint("datetime_stored", "parameter_id", name="unique_observation"),
    )
