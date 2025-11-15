# app/factories/__init__.py
from .song import get_song_dao
from .purchase import get_purchase_dao
# from .rating import get_rating_dao
from .album import get_album_dao

# __all__ = ["get_song_dao", "get_rating_dao"]
__all__ = ["get_song_dao", "get_album_dao"]

