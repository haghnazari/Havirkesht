from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ..models.drivers import Driver


class DriverBase(BaseModel):
    name: str
    last_name: str
    national_code: str
    phone_number: str
    car_id: int
    license_plate: str
    capacity_ton: float


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = None
    last_name: str | None = None
    national_code: str | None = None
    phone_number: str | None = None
    car_id: int | None = None
    license_plate: str | None = None
    capacity_ton: float | None = None


class DriverResponse(BaseModel):
    id: int
    name: str
    last_name: str
    national_code: str
    phone_number: str
    car_id: int
    license_plate: str
    capacity_ton: float
    created_at: datetime

    car_name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_full(cls, d: Driver) -> "DriverResponse":
        return cls(
            id=d.id,
            name=d.name,
            last_name=d.last_name,
            national_code=d.national_code,
            phone_number=d.phone_number,
            car_id=d.car_id,
            license_plate=d.license_plate,
            capacity_ton=d.capacity_ton,
            created_at=d.created_at,
            car_name=d.car.name,
        )
