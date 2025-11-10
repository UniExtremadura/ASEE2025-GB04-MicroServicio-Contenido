import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL")
    upload_dir: str = os.getenv("UPLOAD_DIR", "app/static/uploads")
    file_base_url: str = os.getenv("FILE_BASE_URL", "http://localhost:8080/files")



settings = Settings()

# Extensiones permitidas
ALLOWED_AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg"}
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Límites de tamaño (MB)
MAX_AUDIO_MB = int(os.getenv("MAX_AUDIO_MB", "20"))
MAX_IMAGE_MB = int(os.getenv("MAX_IMAGE_MB", "5"))
