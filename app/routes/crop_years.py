from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError

from ..db import SessionDep
from ..models.crop_years import CropYear
from ..schemas.crop_years import (
    CropYearCreate,
    CropYearResponse,
)
from ..schemas.pagination import Page, paginate

router = APIRouter(
    prefix="/crop-years",
    tags=["Crop Year"],
)

@router.post(
    "/",
    response_model=CropYearResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_crop_year(
    data: CropYearCreate,
    session: SessionDep,
):
    exists = session.scalar(
        select(CropYear).where(
            CropYear.crop_year_name == data.crop_year_name
        )
    )
    if exists:
        raise HTTPException(
            status_code=400,
            detail="Crop year already exists",
        )

    crop_year = CropYear(
        crop_year_name=data.crop_year_name
    )

    session.add(crop_year)
    session.commit()
    session.refresh(crop_year)
    return crop_year


@router.get(
    "/",
    response_model=Page[CropYearResponse],
)
def get_crop_years(
    session: SessionDep,
    page: int = 1,
    size: int = 50,
    sort_by: str | None = None,
    sort_order: str | None = "asc",
    search: str | None = None,
):
    if size > 100:
        size = 100

    stmt = select(CropYear)

    # -------- search --------
    if search:
        stmt = stmt.where(
            CropYear.crop_year_name.ilike(f"%{search}%")
        )

    # -------- sorting --------
    if sort_by == "crop_year_name":
        stmt = stmt.order_by(
            asc(CropYear.crop_year_name)
            if sort_order == "asc"
            else desc(CropYear.crop_year_name)
        )
    else:
        stmt = stmt.order_by(desc(CropYear.created_at))

    total, pages, items = paginate(
        session=session,
        stmt=stmt,
        page=page,
        size=size,
    )

    return Page(
        total=total,
        size=size,
        pages=pages,
        items=items,
    )


@router.delete(
    "/{crop_year_id}",
)
def delete_crop_year(
    crop_year_id: int,
    session: SessionDep,
):
    crop_year = session.get(CropYear, crop_year_id)

    if not crop_year:
        raise HTTPException(
            status_code=404,
            detail="Crop year not found",
        )
    crop_year_name = crop_year.crop_year_name
    session.delete(crop_year)
    session.commit()

    return {
        "message": f"Crop year {crop_year_id}: {crop_year_name} deleted successfully"
    }