# app/api/routes/compras.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.services import auth_proxy as auth
from app.db import get_db
from app.factories.purchase import get_purchase_dao, get_album_purchase_dao
from app.dao.purchase_dao import PurchaseDAO
from app.dao.album_purchase_dao import AlbumPurchaseDAO
from app.models.album import Album
from app.schemas.purchase import (
    CompraCreate,
    CompraOut,
    CompraCheckOut,
    CompraAlbumCreate,
    CompraCheckMultipleIn,
    CompraCheckMultipleOut,
    CompraAlbumOut,
)

router = APIRouter(tags=["compras"])


@router.post(
    "/compras",
    response_model=CompraOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_compra(
    payload: CompraCreate,
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
    identity: dict = Depends(auth.get_current_identity),
):
    # se saca el email del token, que viene de la API de usuarios
    user_email = (identity.get("user_data") or {}).get("email")
    if not user_email:
        raise HTTPException(status_code=400, detail="No se pudo determinar el email del usuario")

    # Si se manda user_ref, debe coincidir con el email del token
    if payload.user_ref and payload.user_ref != user_email:
        raise HTTPException(status_code=403, detail="No puedes comprar en nombre de otro usuario")

    try:
        comp = purchase_dao.purchase(
            song_id=payload.song_id,
            user_ref=user_email,         # EMAIL VERIFICADO
            price_paid=payload.price_paid,
        )
        return comp
    except ValueError as e:
        if str(e) == "song_not_found":
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/compras", response_model=List[int], summary="IDs de canciones compradas por un usuario")
def listar_ids_comprados(
    user_ref: str = Query(..., description="Identificador externo del usuario (email o user_id)"),
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
):
    return purchase_dao.list_user_song_ids(user_ref=user_ref)


@router.get("/compras/check", response_model=CompraCheckOut)
def comprobar_compra(
    user_ref: str = Query(...),
    song_id: int = Query(...),
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
):
    ok = purchase_dao.has_purchase(user_ref=user_ref, song_id=song_id)
    return {"purchased": ok}



@router.post(
    "/albumes/{album_id}/compras",
    response_model=CompraAlbumOut,
    status_code=status.HTTP_201_CREATED,
    summary="Comprar un álbum completo (pay-what-you-want)",
)
async def comprar_album(
    album_id: int,
    payload: CompraAlbumCreate,
    db: Session = Depends(get_db),
    album_purchase_dao: AlbumPurchaseDAO = Depends(get_album_purchase_dao),
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
    identity: dict = Depends(auth.get_current_identity),
):
    user_email = (identity.get("user_data") or {}).get("email")
    if not user_email:
        raise HTTPException(status_code=400, detail="No se pudo determinar el email del usuario")

    # 1) Registrar compra de álbum (cabecera)
    try:
        compra_album = album_purchase_dao.purchase_album(
            album_id=album_id,
            user_ref=user_email,
            price_paid=payload.price_paid,
        )
    except ValueError as e:
        if str(e) == "album_not_found":
            raise HTTPException(status_code=404, detail="Álbum no encontrado")
        if str(e) == "price_below_min":
            raise HTTPException(status_code=400, detail="El precio pagado es inferior al mínimo")
        raise

    # 2) Asegurar compras de todas las canciones (idempotente)
    album = db.query(Album).options(joinedload(Album.canciones)).filter(Album.id == album_id).one()
    for song in album.canciones:
        purchase_dao.purchase(song_id=song.id, user_ref=user_email)

    return compra_album

@router.post(
    "/compras/check-multiple",
    response_model=CompraCheckMultipleOut,
    summary="Comprobar varias compras de canciones",
)
def comprobar_compras_multiples(
    payload: CompraCheckMultipleIn,
    purchase_dao: PurchaseDAO = Depends(get_purchase_dao),
):
    """
    Devuelve qué canciones de `song_ids` tiene compradas el usuario
    y cuáles le faltan (útil para comprobar si posee un álbum completo).
    """
    purchased_ids = set(purchase_dao.list_user_song_ids(user_ref=payload.user_ref))
    requested_ids = set(payload.song_ids)

    owned = sorted(requested_ids & purchased_ids)
    missing = sorted(requested_ids - purchased_ids)

    return {"owned": owned, "missing": missing}
