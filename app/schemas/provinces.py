from pydantic import BaseModel as PydanticBase
from datetime import datetime

class ProvinceCreate(PydanticBase):
    province : str

class ProvinceOut(ProvinceCreate):
    id: int
    created_at: datetime