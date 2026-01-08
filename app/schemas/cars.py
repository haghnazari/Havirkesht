from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CarBase(BaseModel):
    name: str


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    name: str | None = None


class CarResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    #model_config = ConfigDict(from_attributes=True)
