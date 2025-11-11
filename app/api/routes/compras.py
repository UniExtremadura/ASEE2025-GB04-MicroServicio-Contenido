# app/api/routes/compras.py
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.factories.purchase import get_purchase_dao
from app.dao.purchase_dao import PurchaseDAO
from app.schemas.purchase import (
    CompraCreate, CompraOut, CompraCheckOut
)

router = APIRouter(tags=["compras"])


@router.post("/compras", response_model=CompraOut, status_code=status.HTTP_201_CREATED)
def crear_compra(
    payload: CompraCreate,
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
):
    try:
        comp = purchase_dao.purchase(
            song_id=payload.song_id,
            user_ref=payload.user_ref,
            price_paid=payload.price_paid,
        )
        return comp
    except ValueError as e:
        if str(e) == "song_not_found":
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        # Cualquier otro ValueError → 400
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        # por si hay carrera y salta PK/UNIQUE
        raise HTTPException(status_code=409, detail="Compra duplicada") from e
    except Exception as e:
        # ver el mensaje en la respuesta
        raise HTTPException(status_code=500, detail=f"error interno: {e}")



@router.get("/compras", response_model=List[int], summary="IDs de canciones compradas por un usuario")
def listar_ids_comprados(
    user_ref: str = Query(..., description="Identificador externo del usuario (email o user_id)"),
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
):
    return purchase_dao.list_user_song_ids(user_ref=user_ref)

