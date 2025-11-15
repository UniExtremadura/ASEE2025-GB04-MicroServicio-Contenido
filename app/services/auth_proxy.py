# app/services/auth_proxy.py
import os
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import config

security = HTTPBearer(auto_error=False)

async def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta token Bearer")

    token = credentials.credentials
    url = f"{config.settings.users_base_url}/auth/me"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de usuarios no disponible",
        )

    if r.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    # Devuelve { user_type: "user"|"artist", user_data: {...} }
    return r.json()

