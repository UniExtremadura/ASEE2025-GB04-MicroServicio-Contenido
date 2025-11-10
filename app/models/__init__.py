# app/models/__init__.py
from app.db import Base
from .associations import playlist_cancion
from .artist_links import CancionArtistaLink
from .song import Cancion
from .album import Album
from .playlist import Playlist
from .rating import Rating
from .genre import Genre
