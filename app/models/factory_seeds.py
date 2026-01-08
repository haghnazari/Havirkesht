from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime, Float, func
from ..db import Base as SQLAlchemyBase


class FactorySeed(SQLAlchemyBase):
    __tablename__ = "factory_seeds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    factory_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("factories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    seed_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("seeds.id", ondelete="RESTRICT"),
        nullable=False,
    )

    crop_year_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("crop_years.id", ondelete="RESTRICT"),
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)

    farmer_price: Mapped[float] = mapped_column(Float, nullable=False)
    factory_price: Mapped[float] = mapped_column(Float, nullable=False)

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
    factory = relationship("Factory", back_populates="factory_seeds")
    seed = relationship("Seed", back_populates="factory_seeds")
    crop_year = relationship("CropYear", back_populates="factory_seeds")
