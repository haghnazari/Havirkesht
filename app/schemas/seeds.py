from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ..models.seeds import Seed

class SeedBase(BaseModel):
    seed_name: str
    measure_unit_id: int

class SeedCreate(SeedBase):
    pass

class SeedResponse(SeedBase):
    id: int
    created_at: datetime
    unit_name: str | None = None  # optional: نام واحد اندازه‌گیری مرتبط

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_unit(cls, seed: Seed) -> "SeedResponse":
        return cls(
            id=seed.id,
            seed_name=seed.seed_name,
            measure_unit_id=seed.measure_unit_id,
            created_at=seed.created_at,
            unit_name=seed.measure_unit.unit_name if seed.measure_unit else None,
        )