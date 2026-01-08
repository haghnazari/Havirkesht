from ..db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, String, ForeignKey, DateTime, func

class City(SQLAlchemyBase):
    __tablename__ = "cities"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    province = relationship("Province", back_populates="cities")
    villages = relationship("Village", back_populates="city")