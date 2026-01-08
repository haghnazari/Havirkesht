from fastapi import APIRouter, HTTPException, Query
from ..db import SessionDep
from ..schemas.provinces import ProvinceCreate, ProvinceOut
from ..models.provinces import Province
from sqlalchemy import select
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/provinces", tags=["Province"])


@router.post("/", response_model=ProvinceOut)
def create_province(session: SessionDep, province: ProvinceCreate):
    exists = session.execute(
        select(Province).where(Province.province == province.province)
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(status_code=409, detail="Province already exists")

    provinces_query = Province(province=province.province)

    session.add(provinces_query)
    session.commit()
    session.refresh(provinces_query)
    return provinces_query


@router.get("/", response_model=Page[ProvinceOut])
def get_all_provinces(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(Province)
    # -------- search --------
    if search:
        stmt = stmt.where(Province.province.ilike(f"%{search}%"))
    # -------- sorting --------
    allowed_sorts = ["id", "province", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Province, sort_by)
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

@router.delete("/{province_id}")
def delete_province(session: SessionDep, province_id: int):
    province = session.get(Province, province_id)

    if not province:
        raise HTTPException(
            status_code=404,
            detail="Province not found"
        )
    province_name = province.province
    session.delete(province)
    session.commit()

    return {"detail": f"Province {province_id}: {province_name}  deleted successfully"}
