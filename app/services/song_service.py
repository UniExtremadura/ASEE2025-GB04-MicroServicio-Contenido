# app/services/song_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.dao.song_dao import SongDAO
from app.models.song import Cancion

class SongService:
    def __init__(self, db: Session):
        self.song_dao = SongDAO(db)

    def update_song(self, song_id: int, update_data: Dict[str, Any]) -> Optional[Cancion]:
        """
        Servicio para actualizar una canción.
        Por ahora, la lógica es simple y delega en el DAO, pero aquí
        se añadiría lógica de negocio más compleja si fuera necesario.
        """
        # Aquí podrías añadir validaciones de negocio antes de llamar al DAO
        return self.song_dao.update(song_id, update_data=update_data)

    def update_song_price(self, song_id: int, precio: float) -> Optional[Cancion]:
        """Servicio específico para actualizar el precio de una canción."""
        # Llama al método de actualización general del DAO con solo el precio
        return self.song_dao.update(song_id, update_data={"precio": precio})