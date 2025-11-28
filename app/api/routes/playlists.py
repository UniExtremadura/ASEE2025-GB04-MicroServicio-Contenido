# app/api/routes/playlists.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.services import auth_proxy as auth
from app.dao.playlist_dao import PlaylistDAO
from app.factories.playlist import get_playlist_dao
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistOut,
    PlaylistAddSong,
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


def _get_current_email(identity: dict) -> str:
    try:
        return identity["user_data"]["email"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identidad de usuario inválida",
        )


@router.get("", response_model=List[PlaylistOut])
def listar_playlists_propias(
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    """Listar todas las playlists del usuario autenticado."""
    email = _get_current_email(identity)
    playlists = playlist_dao.list_by_owner(owner_ref=email)
    return playlists


@router.post("", response_model=PlaylistOut, status_code=status.HTTP_201_CREATED)
def crear_playlist(
    payload: PlaylistCreate,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    """Crear una nueva playlist para el usuario autenticado."""
    email = _get_current_email(identity)
    playlist = playlist_dao.create(
        owner_ref=email,
        name=payload.name,
        description=payload.description,
        song_ids=payload.song_ids,
    )
    return playlist


@router.get("/{playlist_id}", response_model=PlaylistOut)
def obtener_playlist(
    playlist_id: int,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    playlist = playlist_dao.get(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    email = _get_current_email(identity)
    if playlist.owner_ref != email:
        raise HTTPException(status_code=403, detail="No puedes acceder a esta playlist")

    return playlist


@router.patch("/{playlist_id}", response_model=PlaylistOut)
def actualizar_playlist(
    playlist_id: int,
    payload: PlaylistUpdate,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    playlist = playlist_dao.get(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    email = _get_current_email(identity)
    if playlist.owner_ref != email:
        raise HTTPException(status_code=403, detail="No puedes modificar esta playlist")

    updated = playlist_dao.update(
        playlist_id,
        name=payload.name,
        description=payload.description,
    )
    return updated


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_playlist(
    playlist_id: int,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    playlist = playlist_dao.get(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    email = _get_current_email(identity)
    if playlist.owner_ref != email:
        raise HTTPException(status_code=403, detail="No puedes borrar esta playlist")

    ok = playlist_dao.delete(playlist_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    return None


@router.post("/{playlist_id}/songs", response_model=PlaylistOut)
def anadir_cancion_a_playlist(
    playlist_id: int,
    payload: PlaylistAddSong,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    playlist = playlist_dao.get(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    email = _get_current_email(identity)
    if playlist.owner_ref != email:
        raise HTTPException(status_code=403, detail="No puedes modificar esta playlist")

    try:
        updated = playlist_dao.add_song(playlist_id, payload.song_id)
    except ValueError as e:
        if str(e) == "song_not_found":
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        raise

    return updated


@router.delete("/{playlist_id}/songs/{song_id}", response_model=PlaylistOut)
def eliminar_cancion_de_playlist(
    playlist_id: int,
    song_id: int,
    identity: dict = Depends(auth.get_current_identity),
    playlist_dao: PlaylistDAO = Depends(get_playlist_dao),
):
    playlist = playlist_dao.get(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    email = _get_current_email(identity)
    if playlist.owner_ref != email:
        raise HTTPException(status_code=403, detail="No puedes modificar esta playlist")

    updated = playlist_dao.remove_song(playlist_id, song_id)
    return updated

