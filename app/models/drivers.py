from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Float,
    ForeignKey,
    func,
)
from ..db import Base as SQLAlchemyBase


class Driver(SQLAlchemyBase):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    national_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)

    phone_number: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)

    car_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cars.id", ondelete="RESTRICT"),
        nullable=False,
    )

    license_plate: Mapped[str] = mapped_column(String(20), nullable=False)

    capacity_ton: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -------- relationships --------
    car = relationship("Car", back_populates="drivers")
