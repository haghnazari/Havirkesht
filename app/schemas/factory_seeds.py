from pydantic import BaseModel, ConfigDict
from ..models.factory_seeds import FactorySeed
from datetime import datetime

class FactorySeedBase(BaseModel):
    factory_id: int
    seed_id: int
    crop_year_id: int
    amount: float
    farmer_price: float
    factory_price: float


class FactorySeedCreate(FactorySeedBase):
    pass


class FactorySeedUpdate(BaseModel):
    factory_id: int | None = None
    seed_id: int | None = None
    crop_year_id: int | None = None
    amount: float | None = None
    farmer_price: float | None = None
    factory_price: float | None = None


class FactorySeedResponse(BaseModel):
    id: int
    factory_id: int
    seed_id: int
    crop_year_id: int
    amount: float
    farmer_price: float
    factory_price: float
    created_at: datetime
    updated_at: datetime
    
    factory_name: str
    seed_name: str
    unit_name: str
    crop_year_name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_full(cls, fs: FactorySeed) -> "FactorySeedResponse":
        return cls(
            id=fs.id,
            factory_id=fs.factory_id,
            seed_id=fs.seed_id,
            crop_year_id=fs.crop_year_id,
            amount=fs.amount,
            farmer_price=fs.farmer_price,
            factory_price=fs.factory_price,
            created_at=fs.created_at,
            updated_at=fs.updated_at,
            factory_name=fs.factory.factory_name,
            seed_name=fs.seed.seed_name,
            unit_name=fs.seed.measure_unit.unit_name,
            crop_year_name=fs.crop_year.crop_year_name,
        )
