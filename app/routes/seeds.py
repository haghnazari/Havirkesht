from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionDep
from ..models.seeds import Seed
from ..models.measure_units import MeasureUnit
from ..schemas.seeds import SeedCreate, SeedResponse
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/seeds", tags=["Seed"])


# ---------- Create Seed ----------
@router.post("/", response_model=SeedResponse, status_code=201)
def create_seed(session: SessionDep, seed: SeedCreate):

    if not session.get(MeasureUnit, seed.measure_unit_id):
        raise HTTPException(404, "Measure unit not found")

    exists = session.scalar(select(Seed).where(Seed.seed_name == seed.seed_name))
    if exists:
        raise HTTPException(409, "Seed already exists")

    new_seed = Seed(**seed.model_dump())
    session.add(new_seed)
    session.commit()
    session.refresh(new_seed)

    return SeedResponse.from_orm_with_unit(new_seed)


# ---------- Get all Seeds ----------
@router.get("/", response_model=Page[SeedResponse])
def get_all_seeds(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    measure_unit_id: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = Query("asc", pattern="^(asc|desc)$"),
):

    stmt = select(Seed).options(selectinload(Seed.measure_unit))

    if measure_unit_id:
        stmt = stmt.where(Seed.measure_unit_id == measure_unit_id)

    if search:
        stmt = stmt.where(Seed.seed_name.ilike(f"%{search}%"))

    allowed_sorts = ["id", "seed_name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Seed, sort_by)
        stmt = stmt.order_by(column.desc() if sort_order == "desc" else column)

    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": [
            SeedResponse.from_orm_with_unit(seed)
            for seed in items
        ],
    }


# ---------- Delete Seed ----------
@router.delete("/{seed_id}")
def delete_seed(session: SessionDep, seed_id: int):

    seed = session.get(Seed, seed_id)
    if not seed:
        raise HTTPException(404, "Seed not found")

    seed_name = seed.seed_name
    session.delete(seed)
    session.commit()

    return {"detail": f"Seed {seed_id}:{seed_name} deleted successfully"}
