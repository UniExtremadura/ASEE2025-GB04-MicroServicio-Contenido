# app/services/seed.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.genre import Genre

DEFAULT_GENRES = ["rock", "pop", "reggaeton", "hip hop", "electronic", "jazz", "classical"]

def ensure_seed_genres(db: Session) -> None:
    existing = {
        name for (name,) in db.query(func.lower(Genre.name)).all()
    }
    to_add = [Genre(name=g) for g in DEFAULT_GENRES if g.lower() not in existing]
    if to_add:
        db.add_all(to_add)
        db.commit()

