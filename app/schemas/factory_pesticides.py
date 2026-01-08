from pydantic import BaseModel, ConfigDict
from ..models.factory_pesticides import FactoryPesticide
from datetime import datetime

class FactoryPesticideBase(BaseModel):
    factory_id: int
    pesticide_id: int
    crop_year_id: int
    amount: float
    farmer_price: float
    factory_price: float


class FactoryPesticideCreate(FactoryPesticideBase):
    pass


class FactoryPesticideUpdate(BaseModel):
    factory_id: int | None = None
    pesticide_id: int | None = None
    crop_year_id: int | None = None
    amount: float | None = None
    farmer_price: float | None = None
    factory_price: float | None = None


class FactoryPesticideResponse(BaseModel):
    id: int
    factory_id: int
    pesticide_id: int
    crop_year_id: int
    amount: float
    farmer_price: float
    factory_price: float
    created_at: datetime
    updated_at: datetime
    
    factory_name: str
    pesticide_name: str
    unit_name: str
    crop_year_name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_full(cls, fs: FactoryPesticide) -> "FactoryPesticideResponse":
        return cls(
            id=fs.id,
            factory_id=fs.factory_id,
            pesticide_id=fs.pesticide_id,
            crop_year_id=fs.crop_year_id,
            amount=fs.amount,
            farmer_price=fs.farmer_price,
            factory_price=fs.factory_price,
            created_at=fs.created_at,
            updated_at=fs.updated_at,
            factory_name=fs.factory.factory_name,
            pesticide_name=fs.pesticide.pesticide_name,
            unit_name=fs.pesticide.measure_unit.unit_name,
            crop_year_name=fs.crop_year.crop_year_name,
        )
