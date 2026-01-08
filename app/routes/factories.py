from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from ..db import SessionDep
from ..models.factories import Factory
from ..schemas.factories import FactoryCreate, FactoryResponse
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/factories", tags=["Factory"])


@router.post("/", response_model=FactoryResponse, status_code=201)
def create_factory(
    session: SessionDep,
    factory: FactoryCreate,
):
    # -------- prevent duplicate factory --------
    exists = session.execute(
        select(Factory).where(Factory.factory_name == factory.factory_name)
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=409, detail="Factory already exists."
        )
        
    factory_obj = Factory(
        factory_name=factory.factory_name
    )

    session.add(factory_obj)
    session.commit()
    session.refresh(factory_obj)

    return factory_obj


@router.get("/", response_model=Page[FactoryResponse])
def get_all_factories(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(Factory)

    # -------- search --------
    if search:
        stmt = stmt.where(Factory.factory_name.ilike(f"%{search}%"))

    # -------- sorting --------
    allowed_sorts = ["id", "factory_name", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(Factory, sort_by)
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


@router.delete("/{factory_id}")
def delete_factory(
    session: SessionDep,
    factory_id: int,
):
    factory = session.get(Factory, factory_id)

    if not factory:
        raise HTTPException(
            status_code=404,
            detail="Factory not found."
        )

    factory_name = factory.factory_name
    session.delete(factory)
    session.commit()

    return {"detail": f"Factory {factory_id}: {factory_name} deleted successfully"}