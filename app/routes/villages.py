from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from ..db import SessionDep
from ..models.villages import Village
from ..models.cities import City
from ..schemas.villages import VillageCreate, VillageOut
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/villages", tags=["Village"])


@router.post("/", response_model=VillageOut, status_code=201)
def create_village(
    session: SessionDep,
    village: VillageCreate,
):
    # -------- check city exists --------
    city = session.get(City, village.city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # -------- prevent duplicate villages in same city --------
    exists = session.execute(
        select(Village).where(Village.village == village.village, Village.city_id == village.city_id)
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=409, detail="Village already exists in this city."
        )
        
    village_obj = Village(
        village = village.village,
        city_id=village.city_id
    )

    session.add(village_obj)
    session.commit()
    session.refresh(village_obj)

    return village_obj


@router.get("/", response_model=Page[VillageOut])
def get_all_villages(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    city_id: int | None = None,
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(Village)

    # -------- filter by province --------
    if city_id:
        stmt = stmt.where(Village.city_id == city_id)

    # -------- search --------
    if search:
        stmt = stmt.where(Village.village.ilike(f"%{search}%"))

    # -------- sorting --------
    allowed_sorts = ["id", "village", "created_at", "city_id"]
    if sort_by in allowed_sorts:
        column = getattr(Village, sort_by)
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


@router.delete("/{village_id}")
def delete_city(
    session: SessionDep,
    village_id: int,
):
    village = session.get(Village, village_id)

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found."
        )

    village_name = village.village
    session.delete(village)
    session.commit()

    return {"detail": f"Village {village_id}: {village_name} deleted successfully"}