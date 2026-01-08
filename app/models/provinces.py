from ..db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DateTime, func


class Province(SQLAlchemyBase):

    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    province: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    cities = relationship("City", back_populates="province")
