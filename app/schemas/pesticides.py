from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ..models.pesticides import Pesticide


class PesticideBase(BaseModel):
    pesticide_name: str
    measure_unit_id: int


class PesticideCreate(PesticideBase):
    pass


class PesticideResponse(PesticideBase):
    id: int
    created_at: datetime
    unit_name: str | None = None  # optional: نام واحد اندازه‌گیری مرتبط

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_unit(cls, pesticide: Pesticide) -> "PesticideResponse":
        return cls(
            id=pesticide.id,
            pesticide_name=pesticide.pesticide_name,
            measure_unit_id=pesticide.measure_unit_id,
            created_at=pesticide.created_at,
            unit_name=(
                pesticide.measure_unit.unit_name if pesticide.measure_unit else None
            ),
        )
