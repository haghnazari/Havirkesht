from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DateTime, func
from ..db import Base as SQLAlchemyBase


class MeasureUnit(SQLAlchemyBase):
    __tablename__ = "measure_units"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    unit_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    
    seeds = relationship("Seed", back_populates="measure_unit")
    pesticides = relationship("Pesticide", back_populates="measure_unit")
