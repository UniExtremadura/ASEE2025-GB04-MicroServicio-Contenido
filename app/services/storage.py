from pathlib import Path

from ..config import settings


def save_upload(file, subdir: str) -> str:
    base = Path(settings.upload_dir) / subdir
    base.mkdir(parents=True, exist_ok=True)
    dest = base / file.filename
    with dest.open("wb") as f:
        f.write(file.file.read())
    # devuelve URL pública
    return f"{settings.file_base_url}/{subdir}/{file.filename}"
