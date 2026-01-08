from ..db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DateTime, func


class Factory(SQLAlchemyBase):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    factory_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

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

    factory_seeds = relationship("FactorySeed", back_populates="factory")
    factory_pesticides = relationship("FactoryPesticide", back_populates="factory")
