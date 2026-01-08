from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from ..db import SessionDep
from ..models import FactorySeed, Factory, Seed, CropYear
from ..schemas.factory_seeds import (
    FactorySeedCreate,
    FactorySeedUpdate,
    FactorySeedResponse,
)
from ..schemas.pagination import Page, paginate


router = APIRouter(prefix="/factory_seeds", tags=["Factory Seed"])

@router.post("/", response_model=FactorySeedResponse, status_code=201)
def create_factory_seed(session: SessionDep, data: FactorySeedCreate):
    # existence checks
    if not session.get(Factory, data.factory_id):
        raise HTTPException(status_code=404, detail="Factory not found")

    if not session.get(Seed, data.seed_id):
        raise HTTPException(status_code=404, detail="Seed not found")

    if not session.get(CropYear, data.crop_year_id):
        raise HTTPException(status_code=404, detail="Crop year not found")

    exist = session.scalar(
        select(FactorySeed).where(
            FactorySeed.factory_id == data.factory_id,
            FactorySeed.seed_id == data.seed_id,
            FactorySeed.crop_year_id == data.crop_year_id,
        )
    )
    if exist:
        raise HTTPException(
            status_code=409,
            detail=f"A record for factory {data.factory_id}, seed {data.seed_id}, and crop year {data.crop_year_id} already exists",
        )

    fs = FactorySeed(**data.model_dump())
    session.add(fs)
    session.commit()
    session.refresh(fs)

    return FactorySeedResponse.from_orm_full(fs)

@router.get("/", response_model=Page[FactorySeedResponse])
def get_all_factory_seeds(
    session: SessionDep,
    page: int = 1, 
    size: int = 50,
    factory_id: int | None = None,
    seed_id: int | None = None,
    crop_year_id: int | None = None,
    search: str | None = None,
):
    stmt = select(FactorySeed).options(
        selectinload(FactorySeed.factory),
        selectinload(FactorySeed.seed).selectinload(Seed.measure_unit),
        selectinload(FactorySeed.crop_year),
    )

    if factory_id:
        stmt = stmt.where(FactorySeed.factory_id == factory_id)
    if seed_id:
        stmt = stmt.where(FactorySeed.seed_id == seed_id)
    if crop_year_id:
        stmt = stmt.where(FactorySeed.crop_year_id == crop_year_id)
    if search:
        stmt = stmt.where(
            or_(
                Factory.factory_name.ilike(f"%{search}%"),
                Seed.seed_name.ilike(f"%{search}%"),
                CropYear.crop_year_name.ilike(f"%{search}%"),
            )
        )

    total, pages, items = paginate(session, stmt, page, size)

    return {
        "total": total,
        "size": size,
        "pages": pages,
        "items": [FactorySeedResponse.from_orm_full(fs) for fs in items],
    }



@router.put("/{id}", response_model=FactorySeedResponse)
def update_factory_seed(id: int, session: SessionDep, data: FactorySeedUpdate):
    fs = session.get(FactorySeed, id)
    if not fs:
        raise HTTPException(status_code=404, detail="Factory seed not found")

    exist = session.scalar(
        select(FactorySeed).where(
            FactorySeed.factory_id == data.factory_id,
            FactorySeed.seed_id == data.seed_id,
            FactorySeed.crop_year_id == data.crop_year_id,
        )
    )
    if exist:
        raise HTTPException(
            status_code=409,
            detail=f"A record for factory {data.factory_id}, seed {data.seed_id}, and crop year {data.crop_year_id} already exists",
        )

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(fs, k, v)

    session.commit()
    session.refresh(fs)

    return FactorySeedResponse.from_orm_full(fs)


@router.delete("/{id}")
def delete_factory_seed(id: int, session: SessionDep):
    fs = session.get(FactorySeed, id)
    if not fs:
        raise HTTPException(status_code=404, detail="Factory seed not found")

    session.delete(fs)
    session.commit()
    return {"message": f"Factory seed {id} deleted successfully"}
