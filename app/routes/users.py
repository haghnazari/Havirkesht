from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select
from ..db import SessionDep
from ..schemas.users import UserCreate, UserUpdate, UserResponse
from ..models.users import User
from ..models.roles import Role
from ..schemas.pagination import Page, paginate

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "/admin/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, session: SessionDep):
    stmt = select(User).where(User.username == user.username)
    if session.scalar(stmt):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    stmt = select(User).where(User.email == user.email)
    if session.scalar(stmt):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    stmt = select(User).where(User.phone_number == user.phone_number)
    if session.scalar(stmt):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already exists",
        )

    if not session.get(Role, user.role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not Found.",
        )

    new_user = User(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        password=user.password,  # فعلاً ساده
        disabled=user.disabled,
        role_id=user.role_id,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.get("/", response_model=Page[UserResponse])
def get_all_users(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
):
    stmt = select(User)

    # -------- search --------
    if search:
        stmt = stmt.where(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.fullname.ilike(f"%{search}%"))
        )

    # -------- sorting --------
    allowed_sorts = ["id", "username", "email", "created_at"]
    if sort_by in allowed_sorts:
        column = getattr(User, sort_by)
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


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: SessionDep,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = user_data.model_dump(exclude_unset=True)

    # ---------- username uniqueness ----------
    if "username" in data:
        exists = session.scalar(
            select(User).where(
                User.username == data["username"],
                User.id != user_id,
            )
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Username already exists",
            )

    # ---------- email uniqueness ----------
    if "email" in data:
        exists = session.scalar(
            select(User).where(
                User.email == data["email"],
                User.id != user_id,
            )
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Email already exists",
            )

    # ---------- phone uniqueness ----------
    if "phone_number" in data and data["phone_number"] is not None:
        exists = session.scalar(
            select(User).where(
                User.phone_number == data["phone_number"],
                User.id != user_id,
            )
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Phone number already exists",
            )

    # ---------- role existence ----------
    if "role_id" in data:
        if not session.get(Role, data["role_id"]):
            raise HTTPException(
                status_code=404,
                detail="Role not found",
            )

    # ---------- apply changes ----------
    for field, value in data.items():
        setattr(user, field, value)

    session.commit()
    session.refresh(user)
    return user

@router.patch("/{user_id}/disable", response_model=UserResponse)
def disable_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.disabled = True
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}/enable", response_model=UserResponse)
def enable_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.disabled = False
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(session: SessionDep, user_id: int):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    user_name = user.fullname
    session.delete(user)
    session.commit()

    return {"detail": f"User {user_id}: {user_name}  deleted successfully"}