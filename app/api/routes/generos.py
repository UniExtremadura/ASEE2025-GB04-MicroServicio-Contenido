from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.genre import Genre

router = APIRouter(tags=["generos"])

@router.get("/generos", response_model=list[str])
def listar_generos(db: Session = Depends(get_db)):
    rows = db.query(Genre.name).order_by(Genre.name.asc()).all()
    return [name for (name,) in rows]

