from pydantic import BaseModel as PydanticBase, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(PydanticBase):
    fullname: str = Field(..., min_length=3, max_length=150)
    username: str = Field(..., min_length=4, max_length=50)
    email: EmailStr
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    disabled: bool = False
    role_id: int


class UserUpdate(PydanticBase):
    fullname: Optional[str] = Field(None, min_length=3, max_length=150)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    disabled: Optional[bool] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    disabled: bool
    role_id: int
    created_at: datetime
    updated_at: datetime


class UserLogin(PydanticBase):
    username: str
    password: str
