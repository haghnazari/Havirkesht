from pydantic import BaseModel, Field
from datetime import datetime


# -------- base --------
class CropYearBase(BaseModel):
    crop_year_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        example="1404",
    )


# -------- create --------
class CropYearCreate(CropYearBase):
    pass


# -------- response --------
class CropYearResponse(CropYearBase):
    id: int
    created_at: datetime