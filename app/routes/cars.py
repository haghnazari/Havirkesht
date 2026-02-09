from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import SessionDep
from ..models.cars import Car
from ..schemas.cars import (
    CarCreate,
    CarUpdate,
    CarResponse,
)
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/cars", tags=["Car"])


@router.post("/", response_model=CarResponse, status_code=201)
def create_car(session: SessionDep, data: CarCreate):

    exists = session.scalar(
        select(Car).where(Car.name == data.name)
    )
    if exists:
        raise HTTPException(status_code=409, detail="Car already exists")

    car = Car(**data.model_dump())
    session.add(car)
    session.commit()
    session.refresh(car)

    return car

@router.get("/", response_model=Page[CarResponse])
def get_all_cars(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = Query("asc", pattern="^(asc|desc)$"),
):

    stmt = select(Car)

    if search:
        stmt = stmt.where(Car.name.ilike(f"%{search}%"))

    allowed_sorts = ["id", "name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Car, sort_by)
        stmt = stmt.order_by(
            column.desc() if sort_order == "desc" else column
        )

    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": items,
    }


@router.get("/{car_id}", response_model=CarResponse)
def get_car_by_id(session: SessionDep, car_id: int):

    car = session.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.put("/{car_id}", response_model=CarResponse)
def update_car(
    session: SessionDep,
    car_id: int,
    data: CarUpdate,
):

    car = session.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(car, k, v)

    session.commit()
    session.refresh(car)

    return car


@router.delete("/{car_id}")
def delete_car(session: SessionDep, car_id: int):

    car = session.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    session.delete(car)
    session.commit()

    return {"message": f"Car {car_id} deleted successfully"}
