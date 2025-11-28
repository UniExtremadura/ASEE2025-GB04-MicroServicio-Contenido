# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.db import engine, Base, SessionLocal
import app.models  # <- pobla Base.metadata
from app.api.routes import api_router  # <- agregador /api
from app.services.seed import ensure_seed_genres

app = FastAPI(title="Contenido API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# estáticos
app.mount("/files", StaticFiles(directory="app/static"), name="files")



# Seed para crear los géneros
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    # seed géneros
    with SessionLocal() as db:
        ensure_seed_genres(db)

# rutas
app.include_router(api_router)  # <-- expone /api/canciones, etc.
