from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from ..db import SessionDep
from ..models import Driver, Car
from ..schemas.drivers import (
    DriverCreate,
    DriverUpdate,
    DriverResponse,
)
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/drivers", tags=["Driver"])


@router.post("/", response_model=DriverResponse, status_code=201)
def create_driver(session: SessionDep, data: DriverCreate):

    if not session.get(Car, data.car_id):
        raise HTTPException(status_code=404, detail="Car not found")

    exists = session.scalar(
        select(Driver).where(
            or_(
                Driver.national_code == data.national_code,
                Driver.phone_number == data.phone_number,
            )
        )
    )
    if exists:
        raise HTTPException(
            status_code=409,
            detail="Driver with this national code or phone number already exists",
        )

    driver = Driver(**data.model_dump())
    session.add(driver)
    session.commit()
    session.refresh(driver)

    return DriverResponse.from_orm_full(driver)


@router.get("/", response_model=Page[DriverResponse])
def get_all_drivers(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    car_id: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = Query("asc", pattern="^(asc|desc)$"),
):

    stmt = select(Driver).options(selectinload(Driver.car))

    if car_id:
        stmt = stmt.where(Driver.car_id == car_id)

    if search:
        stmt = stmt.where(
            or_(
                Driver.name.ilike(f"%{search}%"),
                Driver.last_name.ilike(f"%{search}%"),
                Driver.national_code.ilike(f"%{search}%"),
                Driver.phone_number.ilike(f"%{search}%"),
            )
        )

    allowed_sorts = ["id", "name", "last_name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Driver, sort_by)
        stmt = stmt.order_by(column.desc() if sort_order == "desc" else column)

    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": [DriverResponse.from_orm_full(d) for d in items],
    }


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver_by_id(session: SessionDep, driver_id: int):

    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    return DriverResponse.from_orm_full(driver)


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    session: SessionDep,
    driver_id: int,
    data: DriverUpdate,
):

    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(driver, k, v)

    session.commit()
    session.refresh(driver)

    return DriverResponse.from_orm_full(driver)


@router.delete("/{driver_id}")
def delete_driver(session: SessionDep, driver_id: int):

    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver_name = driver.name + " " + driver.last_name

    session.delete(driver)
    session.commit()

    return {"message": f"Driver {driver_id}:{driver_name}  deleted successfully"}