from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from ..db import SessionDep
from ..models import FactoryPesticide, Factory, Pesticide, CropYear
from ..schemas.factory_pesticides import (
    FactoryPesticideCreate,
    FactoryPesticideUpdate,
    FactoryPesticideResponse,
)
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/factory_pesticides", tags=["Factory Pesticide"])

@router.post("/", response_model=FactoryPesticideResponse, status_code=201)
def create_factory_pesticide(session: SessionDep, data: FactoryPesticideCreate):
    # existence checks
    if not session.get(Factory, data.factory_id):
        raise HTTPException(status_code=404, detail="Factory not found")

    if not session.get(Pesticide, data.pesticide_id):
        raise HTTPException(status_code=404, detail="Pesticide not found")

    if not session.get(CropYear, data.crop_year_id):
        raise HTTPException(status_code=404, detail="Crop year not found")

    exist = session.scalar(
        select(FactoryPesticide).where(
            FactoryPesticide.factory_id == data.factory_id,
            FactoryPesticide.pesticide_id == data.pesticide_id,
            FactoryPesticide.crop_year_id == data.crop_year_id,
        )
    )
    if exist:
        raise HTTPException(
            status_code=409,
            detail=f"A record for factory {data.factory_id}, pesticide {data.pesticide_id}, and crop year {data.crop_year_id} already exists",
        )

    fs = FactoryPesticide(**data.model_dump())
    session.add(fs)
    session.commit()
    session.refresh(fs)

    return FactoryPesticideResponse.from_orm_full(fs)


@router.get("/", response_model=Page[FactoryPesticideResponse])
def get_all_factory_pesticides(
    session: SessionDep,
    page: int = 1,
    size: int = 50,
    factory_id: int | None = None,
    pesticide_id: int | None = None,
    crop_year_id: int | None = None,
    search: str | None = None,
):
    stmt = select(FactoryPesticide).options(
        selectinload(FactoryPesticide.factory),
        selectinload(FactoryPesticide.pesticide).selectinload(Pesticide.measure_unit),
        selectinload(FactoryPesticide.crop_year),
    )

    if factory_id:
        stmt = stmt.where(FactoryPesticide.factory_id == factory_id)
    if pesticide_id:
        stmt = stmt.where(FactoryPesticide.pesticide_id == pesticide_id)
    if crop_year_id:
        stmt = stmt.where(FactoryPesticide.crop_year_id == crop_year_id)
    if search:
        stmt = stmt.where(
            or_(
                Factory.factory_name.ilike(f"%{search}%"),
                Pesticide.pesticide_name.ilike(f"%{search}%"),
                CropYear.crop_year_name.ilike(f"%{search}%"),
            )
        )

    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    items = session.scalars(stmt.offset((page - 1) * size).limit(size)).all()

    return {
        "total": total,
        "size": size,
        "pages": (total + size - 1) // size,
        "items": [FactoryPesticideResponse.from_orm_full(fs) for fs in items],
    }


@router.put("/{id}", response_model=FactoryPesticideResponse)
def update_factory_pesticide(id: int, session: SessionDep, data: FactoryPesticideUpdate):
    fs = session.get(FactoryPesticide, id)
    if not fs:
        raise HTTPException(status_code=404, detail="Factory pesticide not found")

    exist = session.scalar(
        select(FactoryPesticide).where(
            FactoryPesticide.factory_id == data.factory_id,
            FactoryPesticide.pesticide_id == data.pesticide_id,
            FactoryPesticide.crop_year_id == data.crop_year_id,
        )
    )
    if exist:
        raise HTTPException(
            status_code=409,
            detail=f"A record for factory {data.factory_id}, pesticide {data.pesticide_id}, and crop year {data.crop_year_id} already exists",
        )

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(fs, k, v)

    session.commit()
    session.refresh(fs)

    return FactoryPesticideResponse.from_orm_full(fs)


@router.delete("/{id}")
def delete_factory_pesticide(id: int, session: SessionDep):
    fs = session.get(FactoryPesticide, id)
    if not fs:
        raise HTTPException(status_code=404, detail="Factory pesticide not found")

    session.delete(fs)
    session.commit()
    return {"message": f"Factory pesticide {id} deleted successfully"}
