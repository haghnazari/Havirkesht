from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from ..db import SessionDep
from ..models.measure_units import MeasureUnit
from ..schemas.measure_units import MeasureUnitCreate, MeasureUnitResponse
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/measure_units", tags=["Measure Unit"])


@router.post("/", response_model=MeasureUnitResponse, status_code=201)
def create_measure_unit(
    session: SessionDep,
    unit: MeasureUnitCreate,
):
    # -------- prevent duplicate unit --------
    exists = session.execute(
        select(MeasureUnit).where(MeasureUnit.unit_name == unit.unit_name)
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=409, detail="Measure unit already exists."
        )
        
    unit_obj = MeasureUnit(
        unit_name=unit.unit_name
    )

    session.add(unit_obj)
    session.commit()
    session.refresh(unit_obj)

    return unit_obj


@router.get("/", response_model=Page[MeasureUnitResponse])
def get_all_measure_units(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(MeasureUnit)

    # -------- search --------
    if search:
        stmt = stmt.where(MeasureUnit.unit_name.ilike(f"%{search}%"))

    # -------- sorting --------
    allowed_sorts = ["id", "unit_name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(MeasureUnit, sort_by)
        if sort_order == "desc":
            column = column.desc()
        stmt = stmt.order_by(column)

    # -------- pagination --------
    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": items,
    }


@router.delete("/{unit_id}")
def delete_measure_unit(
    session: SessionDep,
    unit_id: int,
):
    unit = session.get(MeasureUnit, unit_id)

    if not unit:
        raise HTTPException(
            status_code=404,
            detail="Measure unit not found."
        )

    unit_name = unit.unit_name
    session.delete(unit)
    session.commit()

    return {"detail": f"Measure unit {unit_id}: {unit_name} deleted successfully"}