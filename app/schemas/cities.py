from pydantic import BaseModel as PydanticBase, Field
from datetime import datetime

class CityCreate(PydanticBase):
    city: str = Field(..., min_length=2, max_length=100)
    province_id: int

class CityOut(CityCreate):
    id: int
    city: str
    province_id: int
    created_at: datetime