from pydantic import BaseModel as PydanticBase, Field
from datetime import datetime

class VillageCreate(PydanticBase):
    village: str = Field(..., min_length=2, max_length=100)
    city_id: int

class VillageOut(VillageCreate):
    id: int
    village: str
    city_id: int
    created_at: datetime