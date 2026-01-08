from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from ..db import SessionDep
from ..models.cities import City
from ..models.provinces import Province
from ..schemas.cities import CityCreate, CityOut
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/cities", tags=["City"])


@router.post("/", response_model=CityOut, status_code=201)
def create_city(
    session: SessionDep,
    city: CityCreate,
):
    # -------- check province exists --------
    province = session.get(Province, city.province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    
    # -------- prevent duplicate city in same province --------
    exists = session.execute(
        select(City).where(City.city == city.city, City.province_id == city.province_id)
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=409, detail="City already exists in this province."
        )
        
    city_obj = City(
        city=city.city,
        province_id=city.province_id
    )

    session.add(city_obj)
    session.commit()
    session.refresh(city_obj)

    return city_obj


@router.get("/", response_model=Page[CityOut])
def get_all_cities(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    province_id: int | None = None,
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(City)

    # -------- filter by province --------
    if province_id:
        stmt = stmt.where(City.province_id == province_id)

    # -------- search --------
    if search:
        stmt = stmt.where(City.city.ilike(f"%{search}%"))

    # -------- sorting --------
    allowed_sorts = ["id", "city", "created_at", "province_id"]
    if sort_by in allowed_sorts:
        column = getattr(City, sort_by)
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


@router.delete("/{city_id}")
def delete_city(
    session: SessionDep,
    city_id: int,
):
    city = session.get(City, city_id)

    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found."
        )

    city_name = city.city
    session.delete(city)
    session.commit()

    return {"detail": f"City {city_id}: {city_name} deleted successfully"}