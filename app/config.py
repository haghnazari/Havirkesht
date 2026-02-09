from fastapi import FastAPI
from app.db import create_db_and_tables, SessionLocal, seed_roles
from app.routes import (
    provinces,
    cities,
    villages,
    users,
    crop_years,
    factories,
    measure_units,
    seeds,
    factory_seeds,
    pesticides,
    factory_pesticides,
    cars,
    drivers,
)


app = FastAPI(
    title="Havirkesht", description="Havirkesht: choghandar project!", version="0.0.1"
)


@app.get("/")
def root():
    return {"Project Name": "Havirkesht", "Author": "سعید حق نظری"}


@app.get("/test")
def root():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


app.include_router(users.router)
app.include_router(provinces.router)
app.include_router(cities.router)
app.include_router(villages.router)
app.include_router(crop_years.router)
app.include_router(factories.router)
app.include_router(measure_units.router)
app.include_router(seeds.router)
app.include_router(factory_seeds.router)
app.include_router(pesticides.router)
app.include_router(factory_pesticides.router)
app.include_router(cars.router)
app.include_router(drivers.router)
