from ..db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, func


class Village(SQLAlchemyBase):
    __tablename__ = "villages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    village: Mapped[str] = mapped_column(String, nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    city = relationship("City", back_populates="villages")
