from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, func
from ..db import Base as SQLAlchemyBase

class Seed(SQLAlchemyBase):
    __tablename__ = "seeds"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    seed_name: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True
    )

    measure_unit_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("measure_units.id", ondelete="RESTRICT"), nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    """@property
    def unit_name(self) -> str | None:
        return self.measure_unit.unit_name if self.measure_unit else None"""

    measure_unit = relationship("MeasureUnit", back_populates="seeds")
    factory_seeds = relationship("FactorySeed", back_populates="seed")