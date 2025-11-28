# app/services/storage.py (idea)
from pathlib import Path
import shutil
from fastapi import UploadFile
from app.config import settings  # settings.upload_dir = "app/static/uploads"

BASE = Path(settings.upload_dir)  # app/static/uploads

def save_upload(upload: UploadFile, subdir: str) -> str:
    filename = Path(upload.filename).name
    target_dir = BASE / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / filename
    with dest.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    # lo que guardamos en BD:
    return f"uploads/{subdir}/{filename}"

