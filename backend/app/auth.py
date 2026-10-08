from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    token = settings.api_key
    if not token:
        return True

    auth_header = request.headers.get("authorization") or ""
    if auth_header.startswith("Bearer "):
        provided = auth_header.split(" ", 1)[1].strip()
        if provided == token:
            return True

    if creds and creds.credentials == token:
        return True

    raise HTTPException(status_code=401, detail="Invalid or missing API token")
