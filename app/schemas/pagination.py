from pydantic import BaseModel
from typing import Generic, TypeVar, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    size: int
    pages: int
    items: List[T]


def paginate(
    session: Session,
    stmt,
    page: int,
    size: int,
) -> Tuple[int, int, List[T]]:
    """
    Generic pagination helper
    """

    # -------- total count --------
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.execute(total_stmt).scalar_one()

    # -------- pages --------
    pages = (total + size - 1) // size

    # -------- apply pagination --------
    stmt = stmt.offset((page - 1) * size).limit(size)
    items = session.execute(stmt).scalars().all()

    return total, pages, items
