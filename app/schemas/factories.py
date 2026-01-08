from pydantic import BaseModel as PydanticBase, Field
from datetime import datetime

class FactoryBase(PydanticBase):
    factory_name: str = Field(..., min_length=2, max_length=255)

class FactoryCreate(FactoryBase):
    pass

class FactoryResponse(FactoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
