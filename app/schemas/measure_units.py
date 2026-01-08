from pydantic import BaseModel
from datetime import datetime

class MeasureUnitBase(BaseModel):
    unit_name: str

class MeasureUnitCreate(MeasureUnitBase):
    pass

class MeasureUnitResponse(MeasureUnitBase):
    id: int
    created_at: datetime