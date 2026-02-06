from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/havirkesht"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_session)]


def seed_roles(db: Session):
    from app.models.roles import Role
    roles = [
        {
            "id": 1,
            "name": "پیمانکار/ادمین",
            "scopes": ["admin", "contractor"],
        },
        {
            "id": 2,
            "name": "راننده",
            "scopes": ["driver"],
        },
        {
            "id": 3,
            "name": "کشاورز",
            "scopes": ["farmer"],
        },
    ]

    for role_data in roles:
        exists = db.scalar(
            select(Role).where(Role.id == role_data["id"])
        )
        if not exists:
            db.add(Role(**role_data))

    db.commit()
