# app/api/routes/canciones_upload.py
from __future__ import annotations

from sqlalchemy import func


import inspect
from datetime import date as Date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dao.song_dao import SongDAO
from app.factories import get_song_dao
from app.schemas.song import CancionOut, CancionUpdate, CancionPriceUpdate
from app.services.song_service import SongService
from app.services import storage
from app import config
from app.services.auth_proxy import get_current_identity

from app.models.genre import Genre

router = APIRouter(tags=["canciones"])


def _validate_upload(
    upload: UploadFile | None,
    allowed_exts: set[str],
    max_mb: int,
    kind: str,
    expected_mime_prefix: str,
) -> None:
    """Valida extensión, content-type y tamaño aprox. del archivo subido."""
    if upload is None:
        return
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{kind}: extensión no permitida ({ext}). Permitidas: {sorted(allowed_exts)}",
        )
    ctype = (upload.content_type or "").lower()
    if not ctype.startswith(expected_mime_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{kind}: content-type inválido ({ctype}).",
        )

    # Estimar tamaño leyendo el spooled file
    f = upload.file
    try:
        pos = f.tell()
    except Exception:
        pos = 0
    try:
        f.seek(0, 2)  # EOF
        size_bytes = f.tell()
    finally:
        try:
            f.seek(pos, 0)
        except Exception:
            pass
    max_bytes = max_mb * 1024 * 1024
    if size_bytes and size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{kind}: tamaño {size_bytes // (1024*1024)}MB supera {max_mb}MB.",
        )


async def _save_maybe_async(func, *args, **kwargs) -> str:
    """Compatibilidad: si storage.save_upload es async o sync."""
    res = func(*args, **kwargs)
    if inspect.isawaitable(res):
        return await res
    return res


@router.post(
    "/canciones",
    response_model=CancionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Subida de canción suelta (RF-3.1)",
)
async def upload_cancion(
    nomCancion: str = Form(...),
    precio: float = Form(...),
    genre: Optional[str] = Form(None),
    genres: Optional[List[str]] = Form(None),      # Varios
    date: Optional[Date] = Form(None),
    idAlbum: Optional[int] = Form(None),

    # Puedes enviar varios: artistas_emails=ana@...&artistas_emails=pedro@...
    artistas_emails: Optional[List[str]] = Form(None),

    audio: UploadFile = File(...),
    portada: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    song_dao: SongDAO = Depends(get_song_dao),
    # auth para obtener identidad del que sube
    identity: dict = Depends(get_current_identity),
):


    # Si es artista y no se indicó artistas_emails, usa su email automáticamente
    if identity.get("user_type") == "artist":
        artistas_emails = [identity["user_data"]["email"]]

    # Si es artista y se intentan otros emails, no permitir
    if identity.get("user_type") == "artist" and artistas_emails:
        if identity["user_data"]["email"] not in artistas_emails:
            raise HTTPException(status_code=403, detail="No puedes subir en nombre de otro artista")


    # —— validar nombres de géneros ——
    genre_names = []
    if genres:
        genre_names.extend(genres)
    if genre:                                     # compat: si vino uno solo, también vale
        genre_names.append(genre)

    # elimina duplicados, normaliza
    genre_names = [g.strip() for g in genre_names if g and g.strip()]
    unique_lower = {g.lower() for g in genre_names}
    if unique_lower:
        existing = (
            db.query(Genre)
            .filter(func.lower(Genre.name).in_(list(unique_lower)))
            .all()
        )
        map_lower = {g.name.lower(): g for g in existing}
        missing = sorted(list(unique_lower - set(map_lower.keys())))
        if missing:
            raise HTTPException(400, detail=f"Géneros no válidos: {missing}")

        # normaliza (usa la capitalización exacta de BD)
        genre_names = [map_lower[g.lower()].name for g in genre_names]

        # además, fija el "principal" (campo string) al primero
        if genre_names:
            genre = genre_names[0]


    # 1) Validaciones de archivos
    _validate_upload(audio, config.ALLOWED_AUDIO_EXTS, config.MAX_AUDIO_MB, "audio", "audio/")
    if portada is not None:
        _validate_upload(portada, config.ALLOWED_IMAGE_EXTS, config.MAX_IMAGE_MB, "portada", "image/")

    # 2) Guardado en disco (usa tu servicio existente)
    audio_path = await _save_maybe_async(storage.save_upload, audio, subdir="audio")
    portada_path = None
    if portada:
        portada_path = await _save_maybe_async(storage.save_upload, portada, subdir="img")

    # 3) Persistencia (el DAO solo escribe en su BD)
    song = song_dao.create(
        nomCancion=nomCancion,
        archivoMp3=audio_path,
        imgPortada=portada_path,
        # genre=genre,
        precio=precio,
        date=date,
        artistas_emails=artistas_emails or [],
        idAlbum=idAlbum,
        genre_names=genre_names,            # ← aquí pasan varios

    )

    return song


@router.put(
    "/canciones/{song_id}",
    response_model=CancionOut,
    summary="Actualizar una canción por ID",
)
async def update_cancion(
    song_id: int,
    cancion_update: CancionUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza los campos de una canción.
    Los campos no proporcionados no se modificarán.
    """
    song_service = SongService(db)
    update_data = cancion_update.model_dump(exclude_unset=True)
    updated_song = song_service.update_song(song_id, update_data=update_data)

    if updated_song is None:
        raise HTTPException(status_code=404, detail=f"Canción con id={song_id} no encontrada")

    return updated_song


@router.patch(
    "/canciones/{song_id}/precio",
    response_model=CancionOut,
    summary="Actualizar el precio de una canción",
)
async def update_cancion_price(
    song_id: int,
    price_update: CancionPriceUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza únicamente el precio de una canción específica."""
    song_service = SongService(db)
    updated_song = song_service.update_song_price(song_id, precio=price_update.precio)
    if updated_song is None:
        raise HTTPException(status_code=404, detail=f"Canción con id={song_id} no encontrada")
    return updated_song
