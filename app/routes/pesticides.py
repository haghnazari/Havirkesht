from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionDep
from ..models.pesticides import Pesticide
from ..models.measure_units import MeasureUnit
from ..schemas.pesticides import PesticideCreate, PesticideResponse
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/pesticides", tags=["Pesticide"])


# ---------- Create Pesticide ----------
@router.post("/", response_model=PesticideResponse, status_code=201)
def create_pesticide(session: SessionDep, pesticide: PesticideCreate):

    if not session.get(MeasureUnit, pesticide.measure_unit_id):
        raise HTTPException(404, "Measure unit not found")

    exists = session.scalar(
        select(Pesticide).where(Pesticide.pesticide_name == pesticide.pesticide_name)
    )
    if exists:
        raise HTTPException(409, "Pesticide already exists")

    new_pesticide = Pesticide(**pesticide.model_dump())
    session.add(new_pesticide)
    session.commit()
    session.refresh(new_pesticide)

    return PesticideResponse.from_orm_with_unit(new_pesticide)


# ---------- Get all Pesticides ----------
@router.get("/", response_model=Page[PesticideResponse])
def get_all_pesticides(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    measure_unit_id: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = Query("asc", pattern="^(asc|desc)$"),
):

    stmt = select(Pesticide).options(selectinload(Pesticide.measure_unit))

    if measure_unit_id:
        stmt = stmt.where(Pesticide.measure_unit_id == measure_unit_id)

    if search:
        stmt = stmt.where(Pesticide.pesticide_name.ilike(f"%{search}%"))

    allowed_sorts = ["id", "pesticide_name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Pesticide, sort_by)
        stmt = stmt.order_by(column.desc() if sort_order == "desc" else column)

    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": [
            PesticideResponse.from_orm_with_unit(pesticide) for pesticide in items
        ],
    }


# ---------- Delete Pesticide ----------
@router.delete("/{pesticide_id}")
def delete_pesticide(session: SessionDep, pesticide_id: int):

    pesticide = session.get(Pesticide, pesticide_id)
    if not pesticide:
        raise HTTPException(404, "Pesticide not found")

    pesticide_name = pesticide.pesticide_name
    session.delete(pesticide)
    session.commit()

    return {"detail": f"Pesticide {pesticide_id}:{pesticide_name} deleted successfully"}
